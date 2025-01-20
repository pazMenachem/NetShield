const express = require("express");
const router = express.Router();
const logger = require("../utils/logger");
const userService = require("../services/userService");
const { validateEmail } = require("../middleware/Validations");

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

// // POST /api/users - Create new user
// router.post("/", async (req, res, next) => {

// });

// // PUT /api/users/:id - Update user
// router.put("/:id", async (req, res, next) => {
// });

// // DELETE /api/users/:id - Delete user
// router.delete("/:id", async (req, res, next) => {
// });

module.exports = router;
