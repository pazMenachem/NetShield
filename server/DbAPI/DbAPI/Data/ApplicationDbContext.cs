using Microsoft.EntityFrameworkCore;
using DbAPI.Models;

namespace DbAPI.Data
{
    public class ApplicationDbContext : DbContext
    {
        public ApplicationDbContext(DbContextOptions<ApplicationDbContext> options)
            : base(options)
        {
        }

        public DbSet<User> Users { get; set; } = null!;
        public DbSet<BlockedDomain> BlockedDomains { get; set; } = null!;
        public DbSet<UserSettings> UserSettings { get; set; } = null!;

        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
            base.OnModelCreating(modelBuilder);

            // Configure User
            modelBuilder.Entity<User>(entity =>
            {
                entity.HasIndex(u => u.Email).IsUnique();
                
                // One-to-one relationship with UserSettings
                entity.HasOne(u => u.Settings)
                      .WithOne()
                      .HasForeignKey<UserSettings>(us => us.UserId)
                      .OnDelete(DeleteBehavior.Cascade);
                
                entity.HasMany(u => u.BlockedDomains)
                      .WithOne(bd => bd.User)
                      .HasForeignKey(bd => bd.UserId)
                      .OnDelete(DeleteBehavior.Cascade);
            });

            // Configure UserSettings
            modelBuilder.Entity<UserSettings>(entity =>
            {
                entity.HasKey(e => e.UserId);
                
                entity.Property(e => e.AdultContentBlocked)
                      .HasDefaultValue(false);
                      
                entity.Property(e => e.AdBlocked)
                      .HasDefaultValue(false);
            });

            // Configure BlockedDomain
            modelBuilder.Entity<BlockedDomain>(entity =>
            {
                entity.HasIndex(e => new { e.UserId, e.DomainName }).IsUnique();
            });
        }
    }
}