using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using DbAPI.Data;
using DbAPI.Models;
using DbAPI.Dtos;

namespace DbAPI.Controllers
{
    [ApiController]
    [Route("api/users/{userId}/settings")]
    public class UserSettingsController : ControllerBase
    {
        private readonly ApplicationDbContext _context;
        private readonly ILogger<UserSettingsController> _logger;

        public UserSettingsController(ApplicationDbContext context, ILogger<UserSettingsController> logger)
        {
            _context = context;
            _logger = logger;
        }

        [HttpGet]
        public async Task<ActionResult<UserSettingsDto>> GetSettings(Guid userId)
        {
            var settings = await _context.UserSettings.FindAsync(userId);
            if (settings == null)
            {
                return NotFound("Settings not found");
            }

            return Ok(new UserSettingsDto
            {
                AdultContentBlocked = settings.AdultContentBlocked,
                AdBlocked = settings.AdBlocked
            });
        }

        [HttpPut]
        public async Task<ActionResult<UserSettingsDto>> UpdateSettings(Guid userId, UpdateSettingsDto dto)
        {
            var settings = await _context.UserSettings.FindAsync(userId);
            if (settings == null)
            {
                return NotFound("Settings not found");
            }

            settings.AdultContentBlocked = dto.AdultContentBlocked;
            settings.AdBlocked = dto.AdBlocked;

            try
            {
                await _context.SaveChangesAsync();
            }
            catch (DbUpdateException ex)
            {
                _logger.LogError(ex, "Error updating settings");
                return StatusCode(500, "Internal server error");
            }

            return Ok(new UserSettingsDto
            {
                AdultContentBlocked = settings.AdultContentBlocked,
                AdBlocked = settings.AdBlocked
            });
        }
    }
} 