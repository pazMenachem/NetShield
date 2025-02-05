using System.ComponentModel.DataAnnotations;

namespace DbAPI.Dtos;

public class CreateBlockedDomainDto
{
    private string _domainName = string.Empty;

    private string EnsureWwwPrefix(string domain)
    {
        // If domain doesn't start with www., add it
        if (!domain.StartsWith("www.", StringComparison.OrdinalIgnoreCase))
        {
            return $"www.{domain}";
        }
        return domain;
    }

    private string _backingDomainName = string.Empty;

    [Required]
    [StringLength(255)] 
    [RegularExpression(@"^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$",
        ErrorMessage = "Please enter a valid domain name")]
    public string DomainName
    {
        get => _backingDomainName;
        set => _backingDomainName = EnsureWwwPrefix(value);
    }
}