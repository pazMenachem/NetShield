const grpc = require("@grpc/grpc-js");
const protoLoader = require("@grpc/proto-loader");
const path = require("path");
const fs = require("fs");
const logger = require("../utils/logger");
const config = require("./config");

const PROTO_DIR = path.join(__dirname, "..", "..", "..", "DbAPI", "DbAPI", "Protos");

const loadProtoFiles = () => {
    try {
        // Proto loader options
        const options = {
            keepCase: true,
            longs: String,
            enums: String,
            defaults: true,
            oneofs: true,
            includeDirs: [PROTO_DIR]
        };

        // gRPC channel options
        const channelOptions = {
            "grpc.keepalive_time_ms": 20000,
            "grpc.keepalive_timeout_ms": 10000,
            "grpc.keepalive_permit_without_calls": 1,
            "grpc.http2.min_time_between_pings_ms": 10000,
            "grpc.http2.max_pings_without_data": 0,
            "grpc.max_receive_message_length": -1,
            "grpc.max_send_message_length": -1,
            "grpc.enable_http_proxy": 0,
            "grpc.enable_channelz": 1,
            "grpc.default_compression_algorithm": 0,
            "grpc.max_reconnect_backoff_ms": 1000
        };

        const services = {};
        const protoFiles = fs.readdirSync(PROTO_DIR).filter(file => file.endsWith('.proto'));
        
        for (const file of protoFiles) {
            const serviceName = path.basename(file, '.proto');
            const packageName = serviceName.charAt(0).toUpperCase() + serviceName.slice(1);
            
            console.log(`\n🔍 Processing: ${packageName}`);
            const protoPath = path.join(PROTO_DIR, file);
            const definition = protoLoader.loadSync(protoPath, options);
            const protoObject = grpc.loadPackageDefinition(definition);
            
            const ServiceClass = protoObject[packageName][`${packageName}Service`];
            if (ServiceClass) {
                console.log(`✨ Creating client for: ${packageName}Service`);
                const client = new ServiceClass(
                    config.grpcTarget,
                    grpc.credentials.createInsecure(),
                    channelOptions
                );

                // Enhanced connection test
                const deadline = new Date();
                deadline.setSeconds(deadline.getSeconds() + 5);
                
                client.waitForReady(deadline, (error) => {
                    if (error) {
                        console.error(`❌ Service ${packageName} not ready:`, error);
                        console.error(`Connection target: ${config.grpcTarget}`);
                        console.error('Channel state:', client.getChannel().getConnectivityState(true));
                    } else {
                        console.log(`✅ Service ${packageName} is ready`);
                    }
                });

                services[serviceName] = client;
            }
        }

        return services;
    } catch (error) {
        console.error("❌ Error loading proto files:", error);
        throw error;
    }
};

const services = loadProtoFiles();
module.exports = services; 