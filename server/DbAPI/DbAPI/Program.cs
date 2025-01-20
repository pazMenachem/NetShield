using DbAPI.Data;
using DbAPI.Services;
using dotenv.net;
using Microsoft.EntityFrameworkCore;
using System.Text.Json.Serialization;

DotEnv.Load();

var builder = WebApplication.CreateBuilder(args);

ConfigureServices(builder);
var app = builder.Build();
ConfigureMiddleware(app);
ConfigureEndpoints(app);

app.Run();

// Configure all services
static void ConfigureServices(WebApplicationBuilder builder)
{
    // Add DB Context
    builder.Services.AddDbContext<ApplicationDbContext>(options =>
        options.UseNpgsql(Environment.GetEnvironmentVariable("DB_CONNECTION_STRING") ?? 
        throw new Exception("DB_CONNECTION_STRING is not set")));

    // Add GRPC with options
    builder.Services.AddGrpc();

    // Configure JSON options for REST
    builder.Services.AddControllers()
        .AddJsonOptions(options =>
        {
            options.JsonSerializerOptions.ReferenceHandler = ReferenceHandler.IgnoreCycles;
            options.JsonSerializerOptions.DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull;
        });
    
    builder.Services.AddEndpointsApiExplorer();
    builder.Services.AddSwaggerGen();
}

// Configure middleware pipeline
static void ConfigureMiddleware(WebApplication app)
{
    if (app.Environment.IsDevelopment())
    {
        app.UseSwagger();
        app.UseSwaggerUI();
    }

    app.UseHttpsRedirection();
    app.UseRouting();
    app.UseAuthorization();

    // Request logging middleware
    app.Use(async (context, next) => {
        Console.WriteLine($"Request: {context.Request.Method} {context.Request.Path}");
        await next();
    });
}

// Configure endpoints
static void ConfigureEndpoints(WebApplication app)
{
    // Health check endpoint
    app.MapGet("/", () => "gRPC server running");

    // gRPC services
    app.MapGrpcService<UserService>();
    app.MapGrpcService<SettingsService>();
    app.MapGrpcService<DomainService>();

    // REST endpoints
    app.MapControllers();
}

