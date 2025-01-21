const { domain: domainClient } = require("../config/grpcConfig");

class DomainService {
    blockDomain(email, domain) {
        return new Promise((resolve, reject) => {
            domainClient.blockRemoveDomain({ user_email: email, 
                                            domain: domain, 
                                            to_add: true }, 
                                            (error, response) => {
                error ? reject(error) : resolve(response);
            })
        })
    };

    unblockDomain(email, domain) {
        return new Promise((resolve, reject) => {
            domainClient.blockRemoveDomain({ user_email: email, 
                                             domain: domain, 
                                             to_add: false }, 
                                             (error, response) => {
                error ? reject(error) : resolve(response);
            })
        })
    }
}

module.exports = new DomainService();