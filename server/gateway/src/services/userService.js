const { user: userClient } = require("../config/grpcConfig");

class UserService {
    getUserDetails(email) {
        return new Promise((resolve, reject) => {
            userClient.getUser({ user_email: email }, (error, response) => {
                error ? reject(error) : resolve(response);
            });
        });
    }
    getUsers() {
        return new Promise((resolve, reject) => {
            userClient.getAllUsers({}, (error, response) => {
                error ? reject(error) : resolve(response);
            })
        });
    }

    createUser(email) {
        return new Promise((resolve, reject) => {
            userClient.createDeleteUser({ user_email: email, is_creating: true }, (error, response) => {
                error ? reject(error) : resolve(response);
            })
        });
    };

    deleteUser(email) {
        return new Promise((resolve, reject) => {
            userClient.createDeleteUser({ user_email: email, is_creating: false }, (error, response) => {
                error ? reject(error) : resolve(response);
            })
        });
    }
}

module.exports = new UserService();
