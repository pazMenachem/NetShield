const { settings: settingsClient } = require("../config/grpcConfig");

class SettingsService {
    updateSettings(email, adBlocked, adultContentBlocked) {
        return new Promise((resolve, reject) => {
            settingsClient.updateSettings({ user_email: email, 
                                            ad_blocked: adBlocked, 
                                            adult_content_blocked: adultContentBlocked }, 
                                            (error, response) => {
                error ? reject(error) : resolve(response);
            })
        })
    };
}

module.exports = new SettingsService();
