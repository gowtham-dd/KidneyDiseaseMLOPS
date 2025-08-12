// Main JavaScript for KidneyVision AI

document.addEventListener("DOMContentLoaded", () => {
  // Mobile Navigation Toggle
  const hamburger = document.querySelector(".hamburger")
  const navMenu = document.querySelector(".nav-menu")

  if (hamburger && navMenu) {
    hamburger.addEventListener("click", () => {
      hamburger.classList.toggle("active")
      navMenu.classList.toggle("active")
    })

    // Close mobile menu when clicking on a link
    document.querySelectorAll(".nav-link").forEach((link) => {
      link.addEventListener("click", () => {
        hamburger.classList.remove("active")
        navMenu.classList.remove("active")
      })
    })
  }

  // Flash message close functionality
  const flashCloseButtons = document.querySelectorAll(".flash-close")
  flashCloseButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const flashMessage = button.parentElement
      flashMessage.style.opacity = "0"
      setTimeout(() => {
        flashMessage.remove()
      }, 300)
    })
  })

  // Auto-hide flash messages after 5 seconds
  const flashMessages = document.querySelectorAll(".flash-message")
  flashMessages.forEach((message) => {
    setTimeout(() => {
      message.style.opacity = "0"
      setTimeout(() => {
        if (message.parentElement) {
          message.remove()
        }
      }, 300)
    }, 5000)
  })

  // Smooth scrolling for anchor links
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", function (e) {
      e.preventDefault()
      const target = document.querySelector(this.getAttribute("href"))
      if (target) {
        target.scrollIntoView({
          behavior: "smooth",
          block: "start",
        })
      }
    })
  })

  // Navbar scroll effect
  let lastScrollTop = 0
  const navbar = document.querySelector(".navbar")
  if (navbar) {
    window.addEventListener("scroll", () => {
      const scrollTop = window.pageYOffset || document.documentElement.scrollTop

      if (scrollTop > 100) {
        navbar.style.backgroundColor = "rgba(255, 255, 255, 0.95)"
        navbar.style.backdropFilter = "blur(10px)"
      } else {
        navbar.style.backgroundColor = "#ffffff"
        navbar.style.backdropFilter = "none"
      }

      lastScrollTop = scrollTop
    })
  }

  // Animate elements on scroll
  const observerOptions = {
    threshold: 0.1,
    rootMargin: "0px 0px -50px 0px",
  }

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("fade-in")
      }
    })
  }, observerOptions)

  // Observe elements for animation
  const animateElements = document.querySelectorAll(
    ".feature-card, .condition-card, .application-card, .tech-card, .expertise-card, .stat-card",
  )
  animateElements.forEach((el) => observer.observe(el))

  // Initialize tooltips for technical specifications
  const specItems = document.querySelectorAll(".spec-item")
  specItems.forEach((item) => {
    item.addEventListener("mouseenter", () => {
      item.style.transform = "translateY(-2px)"
      item.style.boxShadow = "0 4px 12px rgba(0, 0, 0, 0.1)"
    })

    item.addEventListener("mouseleave", () => {
      item.style.transform = "translateY(0)"
      item.style.boxShadow = "none"
    })
  })

  // Add loading animation to buttons
  const buttons = document.querySelectorAll(".btn")
  buttons.forEach((button) => {
    button.addEventListener("click", function (e) {
      // Don't add loading state to navigation links
      if (this.classList.contains("nav-link") || this.getAttribute("href")) {
        return
      }

      // Add loading state
      this.classList.add("loading")
      const originalText = this.innerHTML

      // Create loading spinner
      this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...'

      // Remove loading state after 2 seconds (for demo purposes)
      setTimeout(() => {
        this.classList.remove("loading")
        this.innerHTML = originalText
      }, 2000)
    })
  })

  // Keyboard navigation support
  document.addEventListener("keydown", (e) => {
    // ESC key to close modals
    if (e.key === "Escape") {
      const modals = document.querySelectorAll(".modal, .image-modal")
      modals.forEach((modal) => {
        if (modal.style.display === "block") {
          modal.style.display = "none"
        }
      })
    }

    // Enter key for button activation
    if (e.key === "Enter" && e.target.classList.contains("btn")) {
      e.target.click()
    }
  })

  // Add ARIA labels for better accessibility
  const navLinks = document.querySelectorAll(".nav-link")
  navLinks.forEach((link) => {
    if (!link.getAttribute("aria-label")) {
      link.setAttribute("aria-label", `Navigate to ${link.textContent}`)
    }
  })

  // Initialize progress bars with animation
  const progressBars = document.querySelectorAll(".progress-fill")
  progressBars.forEach((bar) => {
    const width = bar.style.width || bar.getAttribute("data-width") || "0%"
    bar.style.width = "0%"
    setTimeout(() => {
      bar.style.width = width
    }, 500)
  })

  // Add hover effects to cards
  const cards = document.querySelectorAll(
    ".feature-card, .condition-card, .tech-card, .application-card, .expertise-card",
  )
  cards.forEach((card) => {
    card.addEventListener("mouseenter", () => {
      card.style.transform = "translateY(-5px)"
    })

    card.addEventListener("mouseleave", () => {
      card.style.transform = "translateY(0)"
    })
  })

  // Initialize confidence bars animation
  const confidenceBars = document.querySelectorAll(".confidence-fill")
  confidenceBars.forEach((bar) => {
    const targetWidth = bar.style.width
    bar.style.width = "0%"
    setTimeout(() => {
      bar.style.width = targetWidth
    }, 1000)
  })

  // Add click tracking for analytics (placeholder)
  document.addEventListener("click", (e) => {
    if (e.target.classList.contains("btn-primary")) {
      console.log("Primary button clicked:", e.target.textContent)
      // Add analytics tracking here
    }
  })

  // Performance optimization - lazy loading for images
  if ("IntersectionObserver" in window) {
    const imageObserver = new IntersectionObserver((entries, observer) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const img = entry.target
          if (img.dataset.src) {
            img.src = img.dataset.src
            img.removeAttribute("data-src")
            imageObserver.unobserve(img)
          }
        }
      })
    })

    document.querySelectorAll("img").forEach((img) => {
      if (img.dataset.src) {
        imageObserver.observe(img)
      }
    })
  }

  // Error handling for images
  document.querySelectorAll("img").forEach((img) => {
    img.addEventListener("error", function () {
      this.src = "/placeholder.svg?height=300&width=400&text=Image+Not+Available"
      this.alt = "Image not available"
    })
  })

  // Form validation helpers
  const forms = document.querySelectorAll("form")
  forms.forEach((form) => {
    form.addEventListener("submit", (e) => {
      const requiredFields = form.querySelectorAll("[required]")
      let isValid = true

      requiredFields.forEach((field) => {
        if (!field.value.trim()) {
          isValid = false
          field.classList.add("error")
          field.addEventListener("input", () => {
            field.classList.remove("error")
          })
        }
      })

      if (!isValid) {
        e.preventDefault()
        showNotification("Please fill in all required fields", "error")
      }
    })
  })

  console.log("MediScan AI interface initialized successfully")
})

// Global notification function
function showNotification(message, type = "info", duration = 5000) {
  const notification = document.createElement("div")
  notification.className = `notification notification-${type}`
  notification.innerHTML = `
    <div class="notification-content">
      <i class="fas fa-${type === "success" ? "check-circle" : type === "error" ? "exclamation-triangle" : "info-circle"}"></i>
      <span>${message}</span>
      <button class="notification-close">&times;</button>
    </div>
  `

  // Add styles
  notification.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    background: ${type === "success" ? "#dcfce7" : type === "error" ? "#fef2f2" : "#eff6ff"};
    color: ${type === "success" ? "#166534" : type === "error" ? "#991b1b" : "#1e40af"};
    border: 1px solid ${type === "success" ? "#bbf7d0" : type === "error" ? "#fecaca" : "#bfdbfe"};
    border-radius: 8px;
    padding: 12px 16px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    z-index: 10000;
    max-width: 400px;
    animation: slideInRight 0.3s ease-out;
  `

  document.body.appendChild(notification)

  // Close button functionality
  const closeBtn = notification.querySelector(".notification-close")
  closeBtn.addEventListener("click", () => {
    notification.remove()
  })

  // Auto remove after duration
  setTimeout(() => {
    if (notification.parentElement) {
      notification.style.animation = "slideOutRight 0.3s ease-in"
      setTimeout(() => {
        notification.remove()
      }, 300)
    }
  }, duration)
}

// Global loading state function
function setLoadingState(element, isLoading) {
  if (!element) return

  if (isLoading) {
    element.disabled = true
    element.classList.add("loading")
    element.dataset.originalText = element.innerHTML
    element.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...'
  } else {
    element.disabled = false
    element.classList.remove("loading")
    element.innerHTML = element.dataset.originalText || element.innerHTML
  }
}

// Add CSS animations
const style = document.createElement("style")
style.textContent = `
  @keyframes slideInRight {
    from {
      transform: translateX(100%);
      opacity: 0;
    }
    to {
      transform: translateX(0);
      opacity: 1;
    }
  }

  @keyframes slideOutRight {
    from {
      transform: translateX(0);
      opacity: 1;
    }
    to {
      transform: translateX(100%);
      opacity: 0;
    }
  }

  .notification-content {
    display: flex;
    align-items: center;
    gap: 10px;
  }

  .notification-close {
    background: none;
    border: none;
    font-size: 1.2rem;
    cursor: pointer;
    color: inherit;
    margin-left: auto;
  }

  .error {
    border-color: #ef4444 !important;
    box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1) !important;
  }
`
document.head.appendChild(style)

// Utility functions
window.MediScanUtils = {
  formatFileSize: (bytes) => {
    if (bytes === 0) return "0 Bytes"
    const k = 1024
    const sizes = ["Bytes", "KB", "MB", "GB"]
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Number.parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i]
  },

  formatDate: (date) =>
    new Date(date).toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    }),

  debounce: (func, wait) => {
    let timeout
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout)
        func(...args)
      }
      clearTimeout(timeout)
      timeout = setTimeout(later, wait)
    }
  },

  throttle: (func, limit) => {
    let inThrottle
    return function () {
      const args = arguments

      if (!inThrottle) {
        func.apply(this, args)
        inThrottle = true
        setTimeout(() => (inThrottle = false), limit)
      }
    }
  },
}
