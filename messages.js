const express = require('express');
const { sendMessage, getMessages, markAsRead, deleteMessage } = require('../controllers/messageController');
const { protect } = require('../middleware/auth');

const router = express.Router();

router.use(protect);

router.post('/', sendMessage);
router.get('/:chatId', getMessages);
router.put('/read/:chatId', markAsRead);
router.delete('/:id', deleteMessage);

module.exports = router;
