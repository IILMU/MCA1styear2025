const express = require('express');
const { getUsers, getUserById, getNotifications, markNotificationsRead } = require('../controllers/userController');
const { protect } = require('../middleware/auth');

const router = express.Router();

router.use(protect);

router.get('/', getUsers);
router.get('/notifications', getNotifications);
router.put('/notifications/read', markNotificationsRead);
router.get('/:id', getUserById);

module.exports = router;
