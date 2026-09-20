const validateEmail = (req, res, next) => {
    const email = req.params.email || req.body.email;

    if (!email) {
        return res.status(400).json({ error: 'Email is required' });
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        return res.status(400).json({ error: 'Invalid email address' });
    }
    next();
}

const validateDomain = (req, res, next) => {
    let domain = req.params.domain || req.body.domain;

    if (!domain) {
        return res.status(400).json({ error: 'Domain is required' });
    }
    if (!domain.startsWith('www.')) {
        domain = `www.${domain}`;
        
        if (req.params.domain) {
            req.params.domain = domain;
        } else {
            req.body.domain = domain;
        }
    }
    next();
}

module.exports = { validateEmail, validateDomain };
