using Grpc.Core;
using Microsoft.EntityFrameworkCore;
using DbAPI.Data;
using DbAPI.Models;
using DbAPI.Protos;

namespace DbAPI.Services;

public class UserService : Protos.UserService.UserServiceBase
{
    private readonly ApplicationDbContext _context;
    private readonly ILogger<UserService> _logger;

    public UserService(ApplicationDbContext context, ILogger<UserService> logger)
    {
        _context = context ?? throw new ArgumentNullException(nameof(context));
        _logger = logger ?? throw new ArgumentNullException(nameof(logger));
    }
    
    #region User CRUD
    /// <summary>
    /// Creates or deletes a user based on the request
    /// </summary>
    /// <exception cref="RpcException">
    ///     Thrown when email is invalid, user already exists (create), 
    ///     user not found (delete), or other errors occur
    /// </exception>
    public override async Task<UserDataResponse> CreateDeleteUser(
        CreateDeleteUserRequest request, 
        ServerCallContext context){
        
        try
        {            
            var user = await _context.Users
                .FirstOrDefaultAsync(u => u.Email == request.UserEmail)
                ?? throw new RpcException(new Status(StatusCode.NotFound, "User not found"));
            
            user = request.IsCreating ? CreateNewUser(request.UserEmail, user) : DeleteUser(user);

            await _context.SaveChangesAsync();
            
            return MapToUserDataResponse(user);
        }
        catch (Exception ex) when (ex is not RpcException)
        {
            _logger.LogError(ex, "Error processing CreateDeleteUser request for email: {Email}", 
                request.UserEmail);
            throw new RpcException(new Status(StatusCode.Internal, "Internal server error"));
        }
    }

    /// <summary>
    /// Retrieves user data based on the provided request
    /// </summary>
    /// <exception cref="RpcException">
    ///     Thrown when email is invalid, user not found, or other errors occur
    /// </exception>
    public override async Task<UserDataResponse> GetUser(
        GetUserDataRequest request, 
        ServerCallContext context){

        try
        {
            var user = await _context.Users
                .Include(u => u.Settings)
                .Include(u => u.BlockedDomains)
                .FirstOrDefaultAsync(u => u.Email == request.UserEmail)
                ?? throw new RpcException(new Status(StatusCode.NotFound, "User not found"));
                
            return MapToUserDataResponse(user);
        }
        catch (Exception ex) when (ex is not RpcException)
        {
            _logger.LogError(ex, "Error processing GetUser request for email: {Email}", request.UserEmail);
            throw new RpcException(new Status(StatusCode.Internal, "Internal server error"));
        }
    }

    /// <summary>
    /// Retrieves all users
    /// </summary>
    /// <exception cref="RpcException">
    ///     Thrown when an internal server error occurs
    /// </exception>
    public override async Task<GetAllUsersResponse> GetAllUsers(GetAllUsersRequest request, ServerCallContext context){
        try{
            var users = await _context.Users
                .Include(u => u.Settings)
                .Include(u => u.BlockedDomains)
                .ToListAsync();

            return new GetAllUsersResponse{
                Users = { users.Select(MapToUserDataResponse) }
            };
        }
        catch (Exception ex) when (ex is not RpcException)
        {
            _logger.LogError(ex, "Error processing GetAllUsers request");
            throw new RpcException(new Status(StatusCode.Internal, "Internal server error"));
        }
    }
    #endregion

    #region Private Methods
    private User CreateNewUser(string email, User user)
    {   
        if (user != null)
            throw new RpcException(new Status(StatusCode.AlreadyExists, "User already exists"));

        var userId = Guid.NewGuid();
        user = new User
        {
            Id = userId,
            Email = email,
            Settings = new UserSettings
            {
                UserId = userId,
                AdultContentBlocked = false,
                AdBlocked = false
            }
        };
        _context.Users.Add(user);
        return user;
    }

    private User DeleteUser(User user){
        if (user == null)
            throw new RpcException(new Status(StatusCode.NotFound, "User not found"));
    
        _context.Users.Remove(user);
        return user;
    }

    private UserDataResponse MapToUserDataResponse(User user){
        return new UserDataResponse
        {
            UserEmail = user.Email,
            UserId = user.Id.ToString(),
            Settings = new Protos.UserSettingsResponse
            {
                AdultContentBlocked = user.Settings?.AdultContentBlocked ?? false,
                AdBlocked = user.Settings?.AdBlocked ?? false
            },
            BlockedDomains = { user.BlockedDomains.Select(d => d.DomainName) }
        };
    }
    #endregion
}
