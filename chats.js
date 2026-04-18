const express = require('express');
const {
  accessChat,
  getChats,
  createGroupChat,
  updateGroupChat,
  addParticipant,
  removeParticipant,
} = require('../controllers/chatController');
const { protect } = require('../middleware/auth');

const router = express.Router();

router.use(protect);

router.route('/').get(getChats).post(accessChat);
router.post('/group', createGroupChat);
router.put('/group/:id', updateGroupChat);
router.put('/group/:id/add', addParticipant);
router.put('/group/:id/remove', removeParticipant);

module.exports = router;
