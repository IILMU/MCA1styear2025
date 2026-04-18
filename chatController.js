const Chat = require('../models/Chat');
const User = require('../models/User');
const Message = require('../models/Message');

// @desc    Access or create 1-1 chat
// @route   POST /api/chats
// @access  Private
const accessChat = async (req, res, next) => {
  try {
    const { userId } = req.body;

    if (!userId) {
      return res.status(400).json({ error: 'userId is required' });
    }

    let chat = await Chat.findOne({
      isGroupChat: false,
      participants: { $all: [req.user._id, userId], $size: 2 },
    })
      .populate('participants', 'username email avatar isOnline lastSeen')
      .populate({ path: 'lastMessage', populate: { path: 'sender', select: 'username avatar' } });

    if (!chat) {
      chat = await Chat.create({
        isGroupChat: false,
        participants: [req.user._id, userId],
      });

      chat = await Chat.findById(chat._id).populate(
        'participants',
        'username email avatar isOnline lastSeen'
      );
    }

    res.json({ chat });
  } catch (err) {
    next(err);
  }
};

// @desc    Get all chats for user
// @route   GET /api/chats
// @access  Private
const getChats = async (req, res, next) => {
  try {
    const chats = await Chat.find({ participants: req.user._id })
      .populate('participants', 'username email avatar isOnline lastSeen')
      .populate('admins', 'username avatar')
      .populate({
        path: 'lastMessage',
        populate: { path: 'sender', select: 'username avatar' },
      })
      .sort({ updatedAt: -1 });

    res.json({ chats });
  } catch (err) {
    next(err);
  }
};

// @desc    Create group chat
// @route   POST /api/chats/group
// @access  Private
const createGroupChat = async (req, res, next) => {
  try {
    const { name, participants, description } = req.body;

    if (!name || !participants || participants.length < 2) {
      return res.status(400).json({ error: 'Group name and at least 2 participants required' });
    }

    const allParticipants = [...new Set([...participants, req.user._id.toString()])];

    const chat = await Chat.create({
      name,
      isGroupChat: true,
      participants: allParticipants,
      admins: [req.user._id],
      createdBy: req.user._id,
      groupDescription: description || '',
    });

    const fullChat = await Chat.findById(chat._id)
      .populate('participants', 'username email avatar isOnline lastSeen')
      .populate('admins', 'username avatar');

    // Create system message
    await Message.create({
      chat: chat._id,
      sender: req.user._id,
      content: `${req.user.username} created the group "${name}"`,
      type: 'system',
    });

    res.status(201).json({ chat: fullChat });
  } catch (err) {
    next(err);
  }
};

// @desc    Update group chat
// @route   PUT /api/chats/group/:id
// @access  Private
const updateGroupChat = async (req, res, next) => {
  try {
    const { name, description, groupAvatar } = req.body;
    const chat = await Chat.findById(req.params.id);

    if (!chat) return res.status(404).json({ error: 'Chat not found' });
    if (!chat.isGroupChat) return res.status(400).json({ error: 'Not a group chat' });
    if (!chat.admins.includes(req.user._id.toString())) {
      return res.status(403).json({ error: 'Only admins can update group' });
    }

    const updates = {};
    if (name) updates.name = name;
    if (description !== undefined) updates.groupDescription = description;
    if (groupAvatar) updates.groupAvatar = groupAvatar;

    const updated = await Chat.findByIdAndUpdate(req.params.id, updates, { new: true })
      .populate('participants', 'username email avatar isOnline lastSeen')
      .populate('admins', 'username avatar');

    res.json({ chat: updated });
  } catch (err) {
    next(err);
  }
};

// @desc    Add participant to group
// @route   PUT /api/chats/group/:id/add
// @access  Private
const addParticipant = async (req, res, next) => {
  try {
    const { userId } = req.body;
    const chat = await Chat.findById(req.params.id);

    if (!chat || !chat.isGroupChat) return res.status(404).json({ error: 'Group not found' });
    if (!chat.admins.includes(req.user._id.toString())) {
      return res.status(403).json({ error: 'Only admins can add members' });
    }

    if (chat.participants.includes(userId)) {
      return res.status(400).json({ error: 'User already in group' });
    }

    const updated = await Chat.findByIdAndUpdate(
      req.params.id,
      { $push: { participants: userId } },
      { new: true }
    )
      .populate('participants', 'username email avatar isOnline lastSeen')
      .populate('admins', 'username avatar');

    const addedUser = await User.findById(userId).select('username');
    await Message.create({
      chat: chat._id,
      sender: req.user._id,
      content: `${req.user.username} added ${addedUser.username} to the group`,
      type: 'system',
    });

    res.json({ chat: updated });
  } catch (err) {
    next(err);
  }
};

// @desc    Remove participant from group
// @route   PUT /api/chats/group/:id/remove
// @access  Private
const removeParticipant = async (req, res, next) => {
  try {
    const { userId } = req.body;
    const chat = await Chat.findById(req.params.id);

    if (!chat || !chat.isGroupChat) return res.status(404).json({ error: 'Group not found' });
    if (!chat.admins.includes(req.user._id.toString()) && req.user._id.toString() !== userId) {
      return res.status(403).json({ error: 'Not authorized' });
    }

    const updated = await Chat.findByIdAndUpdate(
      req.params.id,
      { $pull: { participants: userId } },
      { new: true }
    )
      .populate('participants', 'username email avatar isOnline lastSeen')
      .populate('admins', 'username avatar');

    res.json({ chat: updated });
  } catch (err) {
    next(err);
  }
};

module.exports = { accessChat, getChats, createGroupChat, updateGroupChat, addParticipant, removeParticipant };
