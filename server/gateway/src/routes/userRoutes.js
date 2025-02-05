const express = require("express");
const router = express.Router();
const logger = require("../utils/logger");
const userService = require("../services/userService");
const { validateEmail } = require("../middleware/Validations");

// ********** User routes **********
// GET /api/users/:email
router.get("/:email", validateEmail, async (req, res, next) => {
    try {
        const { email } = req.params;

        const response = await userService.getUserDetails(email);
        
        res.json(response);

    } catch (error) {
        next(error);
    }
});

// POST /api/users - Create new user
router.post("/", validateEmail, async (req, res, next) => {
    try{
        const { email } = req.body;

        const response = await userService.createUser(email);

        res.status(201).json(response);
    } catch (error) {
        next(error);
    }
});

// Need better recognition for user (Token?).
// DELETE /api/users/:email - Delete user
router.delete("/:email", validateEmail, async (req, res, next) => {
    try{
        const { email } = req.params;

        const response = await userService.deleteUser(email);

        res.status(204).json(response);
    } catch (error) {
        next(error);
    }
});

// ********** Admin routes **********
// Won't be used for users.
// Get /api/users
router.get("/", async (req, res, next) => {
    try{
        const response = await userService.getUsers();

        res.json(response);
    } catch (error) {
        next(error);
    }
});

module.exports = router;
