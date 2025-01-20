using Grpc.Core;
using Microsoft.EntityFrameworkCore;
using DbAPI.Data;
using DbAPI.Protos;
using DbAPI.Models;

namespace DbAPI.Services;

public class DomainService : Protos.DomainService.DomainServiceBase
{
    private readonly ApplicationDbContext _context;
    private readonly ILogger<DomainService> _logger;

    public DomainService(ApplicationDbContext context, ILogger<DomainService> logger)
    {
        _context = context;
        _logger = logger;
    }

    public override async Task<BlockRemoveDomainResponse> BlockRemoveDomain(
        BlockRemoveDomainRequest request, 
        ServerCallContext context)
    {
        try
        {
            var user = await _context.Users
                .Include(u => u.BlockedDomains)
                .FirstOrDefaultAsync(u => u.Email == request.UserEmail)
                ?? throw new RpcException(new Status(StatusCode.NotFound, "User not found"));

            if (request.ToAdd)
                BlockDomain(user, request.Domain);
            else
                UnblockDomain(user, request.Domain);
            
            await _context.SaveChangesAsync();
            return new BlockRemoveDomainResponse { Domain = request.Domain };
        }
        catch (Exception ex) when (ex is not RpcException)
        {
            _logger.LogError(ex, "Error processing BlockDomain request for email: {Email}", request.UserEmail);
            throw new RpcException(new Status(StatusCode.Internal, "Internal server error"));
        }
    }

    private static void BlockDomain(User user, string domain)
    {
        if (user.BlockedDomains.Any(d => d.DomainName == domain))
            throw new RpcException(new Status(StatusCode.AlreadyExists, "Domain already blocked"));
        
        user.BlockedDomains.Add(new BlockedDomain { DomainName = domain, UserId = user.Id });
    }

    private static void UnblockDomain(User user, string domain)
    {
        var blockedDomain = user.BlockedDomains.FirstOrDefault(d => d.DomainName == domain)
            ?? throw new RpcException(new Status(StatusCode.NotFound, "Domain not found in blocked list"));
        
        user.BlockedDomains.Remove(blockedDomain);
    }
} 