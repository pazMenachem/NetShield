const express = require("express");
const router = express.Router();
const logger = require("../utils/logger");
const domainService = require("../services/domainService");
const { validateEmail, validateDomain } = require("../middleware/Validations");

// POST /api/domains/:email/:domain - Block domain
router.post("/:email/:domain", validateEmail, validateDomain, async (req, res, next) => {
    try{
        const { email, domain } = req.params;

        const response = await domainService.blockDomain(email, domain);

        res.status(201).json(response);
    } catch (error) {
        next(error);
    }
});

// DELETE /api/domains/:email/:domain - Unblock domain
router.delete("/:email/:domain", validateEmail, validateDomain, async (req, res, next) => {
    try{
        const { email, domain } = req.params;

        const response = await domainService.unblockDomain(email, domain);

        res.status(204).json(response);
    } catch (error) {
        next(error);
    }
});

module.exports = router;
