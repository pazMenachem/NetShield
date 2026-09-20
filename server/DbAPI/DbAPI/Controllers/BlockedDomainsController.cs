using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using DbAPI.Data;
using DbAPI.Models;
using DbAPI.Dtos;

namespace DbAPI.Controllers
{
    [ApiController]
    [Route("api/users/{userId}/[controller]")]
    public class BlockedDomainsController : ControllerBase
    {
        private readonly ApplicationDbContext _context;
        private readonly ILogger<BlockedDomainsController> _logger;

        public BlockedDomainsController(ApplicationDbContext context, ILogger<BlockedDomainsController> logger)
        {
            _context = context;
            _logger = logger;
        }

        [HttpGet]
        public async Task<ActionResult<IEnumerable<BlockedDomain>>> GetBlockedDomains(Guid userId)
        {
            if (!await _context.Users.AnyAsync(u => u.Id == userId))
            {
                return NotFound("User not found");
            }

            return await _context.BlockedDomains
                .Where(bd => bd.UserId == userId)
                .ToListAsync();
        }

        [HttpPost]
        public async Task<ActionResult<BlockedDomain>> AddBlockedDomain(
            Guid userId, 
            [FromBody] CreateBlockedDomainDto dto)
        {
            if (!await _context.Users.AnyAsync(u => u.Id == userId))
            {
                return NotFound("User not found");
            }

            var blockedDomain = new BlockedDomain
            {
                Id = Guid.NewGuid(),
                UserId = userId,
                DomainName = dto.DomainName
            };

            _context.BlockedDomains.Add(blockedDomain);
            try
            {
                await _context.SaveChangesAsync();
            }
            catch (DbUpdateException)
            {
                return Conflict("Domain already blocked for this user");
            }

            return Ok(blockedDomain);
        }

        [HttpDelete("{domainName}")]
        public async Task<IActionResult> RemoveBlockedDomain(Guid userId, string domainName)
        {
            var blockedDomain = await _context.BlockedDomains
                .FirstOrDefaultAsync(bd => bd.UserId == userId && bd.DomainName == domainName);

            if (blockedDomain == null)
            {
                return NotFound("Blocked domain not found");
            }

            _context.BlockedDomains.Remove(blockedDomain);
            await _context.SaveChangesAsync();

            return NoContent();
        }
    }
} 