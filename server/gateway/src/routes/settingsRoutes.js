const express = require("express");
const router = express.Router();
const logger = require("../utils/logger");
const settingsService = require("../services/settingsService");
const { validateEmail } = require("../middleware/Validations");

// PUT /api/settings/ - Update settings
router.put("/", validateEmail, async (req, res, next) => {
    try{
        const { email, ad_blocked, adult_content_blocked } = req.body;

        const response = await settingsService.updateSettings(email, ad_blocked, adult_content_blocked);

        res.status(201).json(response);
    } catch (error) {
        next(error);
    }
});

module.exports = router;