using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using DbAPI.Data;
using DbAPI.Models;
using DbAPI.Dtos;

namespace DbAPI.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class UsersController : ControllerBase
    {
        private readonly ApplicationDbContext _context;
        private readonly ILogger<UsersController> _logger;

        public UsersController(ApplicationDbContext context, ILogger<UsersController> logger)
        {
            _context = context;
            _logger = logger;
        }

        [HttpGet]
        public async Task<ActionResult<IEnumerable<UserResponseDto>>> GetUsers()
        {
            var users = await _context.Users
                .Include(u => u.Settings)
                .Include(u => u.BlockedDomains)
                .Select(u => new UserResponseDto
                {
                    Id = u.Id,
                    Email = u.Email,
                    Settings = u.Settings != null ? new UserSettingsDto
                    {
                        AdultContentBlocked = u.Settings.AdultContentBlocked,
                        AdBlocked = u.Settings.AdBlocked
                    } : null,
                    BlockedDomains = u.BlockedDomains.Select(bd => new BlockedDomainResponseDto
                    {
                        DomainName = bd.DomainName
                    }).ToList()
                })
                .ToListAsync();

            return Ok(users);
        }

        [HttpPost]
        public async Task<ActionResult<UserResponseDto>> CreateUser(CreateUserDto dto)
        {
            var userId = Guid.NewGuid();
            var user = new User
            {
                Id = userId,
                Email = dto.Email,
                Settings = new UserSettings
                {
                    UserId = userId,
                    AdultContentBlocked = false,
                    AdBlocked = false
                }
            };

            _context.Users.Add(user);
            await _context.SaveChangesAsync();

            return CreatedAtAction(nameof(GetUser), 
                new { id = user.Id }, 
                new UserResponseDto
                {
                    Id = user.Id,
                    Email = user.Email,
                    Settings = new UserSettingsDto
                    {
                        AdultContentBlocked = user.Settings.AdultContentBlocked,
                        AdBlocked = user.Settings.AdBlocked
                    },
                    BlockedDomains = new List<BlockedDomainResponseDto>()
                });
        }

        [HttpGet("{id}")]
        public async Task<ActionResult<UserResponseDto>> GetUser(Guid id)
        {
            var user = await _context.Users
                .Include(u => u.Settings)
                .Include(u => u.BlockedDomains)
                .FirstOrDefaultAsync(u => u.Id == id);

            if (user == null)
            {
                return NotFound();
            }

            var response = new UserResponseDto
            {
                Id = user.Id,
                Email = user.Email,
                Settings = user.Settings != null ? new UserSettingsDto
                {
                    AdultContentBlocked = user.Settings.AdultContentBlocked,
                    AdBlocked = user.Settings.AdBlocked
                } : null,
                BlockedDomains = user.BlockedDomains.Select(bd => new BlockedDomainResponseDto
                {
                    DomainName = bd.DomainName
                }).ToList()
            };

            return Ok(response);
        }

        [HttpDelete("{id}")]
        public async Task<IActionResult> DeleteUser(Guid id)
        {
            var user = await _context.Users
                .Include(u => u.Settings)
                .Include(u => u.BlockedDomains)
                .FirstOrDefaultAsync(u => u.Id == id);

            if (user == null)
            {
                return NotFound("User not found");
            }

            try
            {
                _context.Users.Remove(user);
                await _context.SaveChangesAsync();
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error deleting user");
                return StatusCode(500, "Internal server error while deleting user");
            }

            return NoContent();  // 204 No Content is standard for successful DELETE
        }
    }
} 