const validateEmail = (req, res, next) => {
    if (!req.params.email) {
        return res.status(400).json({ error: 'Email is required' });
    }
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(req.params.email)) {
        return res.status(400).json({ error: 'Invalid email address' });
    }
    next();
}

module.exports = { validateEmail };