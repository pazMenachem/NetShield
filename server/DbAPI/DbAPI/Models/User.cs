using System.ComponentModel.DataAnnotations;
using System.Text.Json.Serialization;

namespace DbAPI.Models
{
    // Later on - add password hash and salt
    public class User
    {
        [Key]
        public Guid Id { get; set; }

        [Required]
        [EmailAddress]
        public required string Email { get; set; }

        public UserSettings? Settings { get; set; }
        
        [JsonIgnore]
        public ICollection<BlockedDomain> BlockedDomains { get; set; } = new List<BlockedDomain>();
    }
}