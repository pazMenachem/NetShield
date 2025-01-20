using System.ComponentModel.DataAnnotations;

namespace DbAPI.Dtos;

public class CreateUserDto
{
    [Required]
    [EmailAddress]
    public required string Email { get; set; }
}