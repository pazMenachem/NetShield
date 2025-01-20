const logger = require('../utils/logger');

module.exports = (err, req, res) => {
    logger.error('Error:', {
        message: err.message,
        stack: err.stack,
        path: req.path
        });
    
        res.status(err.status || 500).json({
            error: {
                message: err.message || 'Internal server error',
                status: err.status || 500
            }
        });
};

