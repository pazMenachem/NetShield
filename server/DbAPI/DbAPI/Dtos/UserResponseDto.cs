using System.ComponentModel.DataAnnotations;

namespace DbAPI.Dtos;

public class UserResponseDto
{
    public Guid Id { get; set; }
    public required string Email { get; set; }
    public UserSettingsDto? Settings { get; set; }
    public ICollection<BlockedDomainResponseDto> BlockedDomains { get; set; } = new List<BlockedDomainResponseDto>();
}

public class UserSettingsDto
{
    public bool AdultContentBlocked { get; set; }
    public bool AdBlocked { get; set; }
}

public class BlockedDomainResponseDto
{
    public required string DomainName { get; set; }
} 