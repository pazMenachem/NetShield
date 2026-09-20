require('dotenv').config();

const port = process.env.PORT || 3000;
const grpcTarget = process.env.GRPC_DB_API || "localhost:5093";
const nodeEnv = process.env.NODE_ENV || "development";

// Add validation
if (!grpcTarget) {
    throw new Error('GRPC_DB_API environment variable is required');
}

console.log('gRPC Target:', grpcTarget); // For debugging

module.exports = { port, grpcTarget, nodeEnv };
