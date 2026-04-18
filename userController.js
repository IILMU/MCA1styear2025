const User = require('../models/User');

// @desc    Get all users (for search)
// @route   GET /api/users?search=query
// @access  Private
const getUsers = async (req, res, next) => {
  try {
    const { search } = req.query;
    const query = {
      _id: { $ne: req.user._id },
    };

    if (search) {
      query.$or = [
        { username: { $regex: search, $options: 'i' } },
        { email: { $regex: search, $options: 'i' } },
      ];
    }

    const users = await User.find(query)
      .select('username email avatar isOnline lastSeen bio')
      .limit(20)
      .lean();

    res.json({ users });
  } catch (err) {
    next(err);
  }
};

// @desc    Get user by ID
// @route   GET /api/users/:id
// @access  Private
const getUserById = async (req, res, next) => {
  try {
    const user = await User.findById(req.params.id).select(
      'username email avatar isOnline lastSeen bio createdAt'
    );

    if (!user) {
      return res.status(404).json({ error: 'User not found' });
    }

    res.json({ user });
  } catch (err) {
    next(err);
  }
};

// @desc    Get notifications
// @route   GET /api/users/notifications
// @access  Private
const getNotifications = async (req, res, next) => {
  try {
    const user = await User.findById(req.user._id)
      .populate('notifications.from', 'username avatar')
      .populate('notifications.chat', 'name isGroupChat');

    const notifications = user.notifications
      .sort((a, b) => b.createdAt - a.createdAt)
      .slice(0, 50);

    res.json({ notifications });
  } catch (err) {
    next(err);
  }
};

// @desc    Mark notifications as read
// @route   PUT /api/users/notifications/read
// @access  Private
const markNotificationsRead = async (req, res, next) => {
  try {
    await User.findByIdAndUpdate(req.user._id, {
      $set: { 'notifications.$[].read': true },
    });

    res.json({ message: 'Notifications marked as read' });
  } catch (err) {
    next(err);
  }
};

module.exports = { getUsers, getUserById, getNotifications, markNotificationsRead };
