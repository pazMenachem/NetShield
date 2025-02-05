using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace DbAPI.Models
{
    public class BlockedDomain
    {
        [Key]
        public Guid Id { get; set; }

        [Required]
        [StringLength(255)]
        public required string DomainName { get; set; }

        [Required]
        public Guid UserId { get; set; }

        [ForeignKey(nameof(UserId))]
        public User? User { get; set; }
    }
}
