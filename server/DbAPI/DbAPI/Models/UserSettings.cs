using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace DbAPI.Models
{
    public class UserSettings
    {
        [Key]
        public Guid UserId { get; set; }

        [Required]
        public bool AdultContentBlocked { get; set; }

        [Required]
        public bool AdBlocked { get; set; }
    }
}