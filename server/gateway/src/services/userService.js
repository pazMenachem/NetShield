const { user: userClient } = require("../config/grpcConfig");
const logger = require("../utils/logger");

class UserService {
    getUserDetails(email) {
        return new Promise((resolve, reject) => {
            userClient.getUser({ user_email: email }, (error, response) => {
                error ? reject(error) : resolve(response);
            });
        });
    }
}

module.exports = new UserService(); 