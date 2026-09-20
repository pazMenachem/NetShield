const express = require("express");
const userRoutes = require("./routes/userRoutes");
const domainRoutes = require("./routes/domainRoutes");
const settingsRoutes = require("./routes/settingsRoutes");
const errorHandler = require("./middleware/errorHandler");

const app = express();

app.use(express.json());

// Routes
app.use("/api/users", userRoutes);
app.use("/api/domains", domainRoutes);
app.use("/api/settings", settingsRoutes);

// Error handling
app.use(errorHandler);

module.exports = app;
