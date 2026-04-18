const Message = require('../models/Message');
const Chat = require('../models/Chat');
const User = require('../models/User');
const { encrypt, decrypt } = require('../utils/encryption');

// @desc    Send a message
// @route   POST /api/messages
// @access  Private
const sendMessage = async (req, res, next) => {
  try {
    const { chatId, content, type = 'text', replyTo, fileData } = req.body;

    if (!chatId) {
      return res.status(400).json({ error: 'chatId is required' });
    }

    if (!content && !fileData) {
      return res.status(400).json({ error: 'Message content or file is required' });
    }

    const chat = await Chat.findOne({
      _id: chatId,
      participants: req.user._id,
    });

    if (!chat) {
      return res.status(404).json({ error: 'Chat not found or access denied' });
    }

    const messageData = {
      chat: chatId,
      sender: req.user._id,
      type,
    };

    if (content) {
      messageData.content = content;
      messageData.encryptedContent = encrypt(content);
    }

    if (fileData) {
      messageData.file = fileData;
    }

    if (replyTo) {
      messageData.replyTo = replyTo;
    }

    let message = await Message.create(messageData);

    message = await Message.findById(message._id)
      .populate('sender', 'username avatar')
      .populate('replyTo', 'content sender type')
      .populate({ path: 'replyTo', populate: { path: 'sender', select: 'username' } });

    // Update chat's lastMessage
    await Chat.findByIdAndUpdate(chatId, { lastMessage: message._id });

    // Add notification for other participants
    const otherParticipants = chat.participants.filter(
      (p) => p.toString() !== req.user._id.toString()
    );

    await User.updateMany(
      { _id: { $in: otherParticipants } },
      {
        $push: {
          notifications: {
            type: 'message',
            from: req.user._id,
            chat: chatId,
            message: content ? content.substring(0, 50) : 'Sent a file',
            read: false,
            createdAt: new Date(),
          },
        },
      }
    );

    res.status(201).json({ message });
  } catch (err) {
    next(err);
  }
};

// @desc    Get messages for a chat
// @route   GET /api/messages/:chatId
// @access  Private
const getMessages = async (req, res, next) => {
  try {
    const { chatId } = req.params;
    const { page = 1, limit = 50 } = req.query;

    const chat = await Chat.findOne({
      _id: chatId,
      participants: req.user._id,
    });

    if (!chat) {
      return res.status(404).json({ error: 'Chat not found or access denied' });
    }

    const messages = await Message.find({ chat: chatId, isDeleted: false })
      .populate('sender', 'username avatar')
      .populate({
        path: 'replyTo',
        populate: { path: 'sender', select: 'username' },
        select: 'content sender type file',
      })
      .populate('readBy.user', 'username avatar')
      .sort({ createdAt: -1 })
      .skip((page - 1) * limit)
      .limit(parseInt(limit));

    const total = await Message.countDocuments({ chat: chatId, isDeleted: false });

    res.json({
      messages: messages.reverse(),
      pagination: {
        page: parseInt(page),
        limit: parseInt(limit),
        total,
        hasMore: page * limit < total,
      },
    });
  } catch (err) {
    next(err);
  }
};

// @desc    Mark messages as read
// @route   PUT /api/messages/read/:chatId
// @access  Private
const markAsRead = async (req, res, next) => {
  try {
    const { chatId } = req.params;

    await Message.updateMany(
      {
        chat: chatId,
        sender: { $ne: req.user._id },
        'readBy.user': { $ne: req.user._id },
        isDeleted: false,
      },
      {
        $push: {
          readBy: { user: req.user._id, readAt: new Date() },
        },
      }
    );

    res.json({ message: 'Messages marked as read' });
  } catch (err) {
    next(err);
  }
};

// @desc    Delete a message
// @route   DELETE /api/messages/:id
// @access  Private
const deleteMessage = async (req, res, next) => {
  try {
    const message = await Message.findById(req.params.id);

    if (!message) return res.status(404).json({ error: 'Message not found' });
    if (message.sender.toString() !== req.user._id.toString()) {
      return res.status(403).json({ error: 'Not authorized to delete this message' });
    }

    message.isDeleted = true;
    message.deletedAt = new Date();
    message.content = '';
    message.encryptedContent = '';
    await message.save();

    res.json({ message: 'Message deleted' });
  } catch (err) {
    next(err);
  }
};

module.exports = { sendMessage, getMessages, markAsRead, deleteMessage };
