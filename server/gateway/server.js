const app = require("./src/app");
const config = require("./src/config/config");
const logger = require("./src/utils/logger");

let server;

/**
 * Starts the server and initializes event handlers
*/
function serverStart() {
    try {
        // Start the server
        server = app.listen(config.port, onServerStart);
        
        // Initialize event handlers
        initEvents();
        
        logger.info("Server initialization completed");
    } catch (error) {
        logger.error("Server initialization failed:", error);
        process.exit(1);
    }
}

/**
 * Sets up basic server event handlers
 */
function initEvents() {
    // Graceful shutdown handler
    process.on("SIGTERM", () => {
        logger.info("SIGTERM signal received: closing HTTP server");
        server.close(() => {
            logger.info("HTTP server closed");
            process.exit(0);
        });
    });

    // Unexpected error handler
    process.on("uncaughtException", (error) => {
        logger.error("Uncaught Exception:", error);
        process.exit(1);
    });
}

/**
 * Callback function that runs when server starts successfully
 */
function onServerStart() {
    logger.info(`Gateway server running on port ${config.port}`);
}

// Start the server
serverStart();
