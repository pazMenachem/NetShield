using System.ComponentModel.DataAnnotations;

namespace DbAPI.Dtos;

public class UpdateSettingsDto
{
    [Required]
    public bool AdultContentBlocked { get; set; }
    
    [Required]
    public bool AdBlocked { get; set; }
} 