using Grpc.Core;
using Microsoft.EntityFrameworkCore;
using DbAPI.Data;
using DbAPI.Protos;

namespace DbAPI.Services;

public class SettingsService : Protos.SettingsService.SettingsServiceBase
{
    private readonly ApplicationDbContext _context;
    private readonly ILogger<SettingsService> _logger;

    public SettingsService(ApplicationDbContext context, ILogger<SettingsService> logger)
    {
        _context = context ?? throw new ArgumentNullException(nameof(context));
        _logger = logger ?? throw new ArgumentNullException(nameof(logger));
    }

    public override async Task<UpdateSettingsResponse> UpdateSettings(
        UpdateSettingsRequest request,
        ServerCallContext context)
    {
        try
        {
            var user = await _context.Users
                .Where(u => u.Email == request.UserEmail)
                .Include(u => u.Settings)
                .FirstOrDefaultAsync() ??
                throw new RpcException(new Status(StatusCode.NotFound, "User not found"));

            user.Settings!.AdBlocked = request.AdBlocked;
            user.Settings!.AdultContentBlocked = request.AdultContentBlocked;

            await _context.SaveChangesAsync();
            return new UpdateSettingsResponse {};
        }
        catch (Exception ex) when (ex is not RpcException)
        {
            _logger.LogError(ex, "Error processing UpdateSettings request");
            throw new RpcException(new Status(StatusCode.Internal, "Internal server error"));
        }
    }
} 