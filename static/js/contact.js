// Contact page specific JavaScript functionality

document.addEventListener("DOMContentLoaded", () => {
    initializeContactPage()
    console.log("MediScan AI - Contact page initialized")
  })
  
  function initializeContactPage() {
    initializeContactForm()
    initializeContactMethods()
    initializeFormValidation()
    initializeEmergencyContact()
    initializeHoverEffects()
  }
  
  // Contact form functionality
  function initializeContactForm() {
    const contactForm = document.getElementById("contactForm")
    const submitBtn = document.getElementById("submitContactForm")
  
    if (contactForm) {
      contactForm.addEventListener("submit", handleContactFormSubmission)
    }
  
    // Real-time form validation
    const formInputs = contactForm?.querySelectorAll("input, select, textarea")
    formInputs?.forEach((input) => {
      input.addEventListener("blur", validateFormField)
      input.addEventListener("input", clearFieldError)
    })
  }
  
  function handleContactFormSubmission(e) {
    e.preventDefault()
  
    const formData = new FormData(e.target)
    const contactData = {
      name: formData.get("name"),
      email: formData.get("email"),
      organization: formData.get("organization"),
      inquiryType: formData.get("inquiry_type"),
      message: formData.get("message"),
      urgent: formData.get("urgent") === "on",
    }
  
    // Validate all fields
    if (!validateContactForm(contactData)) {
      return
    }
  
    // Show loading state
    const submitBtn = document.getElementById("submitContactForm")
    setLoadingState(submitBtn, true)
  
    // Simulate form submission (replace with actual API call)
    setTimeout(() => {
      // Success simulation
      showNotification("Thank you for your inquiry. Our medical team will contact you within 24 hours.", "success")
  
      // Reset form
      e.target.reset()
      setLoadingState(submitBtn, false)
  
      // Log inquiry for medical professionals
      logMedicalInquiry(contactData)
    }, 2000)
  }
  
  function validateContactForm(data) {
    let isValid = true
  
    // Name validation
    if (!data.name || data.name.trim().length < 2) {
      showFieldError("name", "Please enter your full name")
      isValid = false
    }
  
    // Email validation
    if (!data.email || !isValidEmail(data.email)) {
      showFieldError("email", "Please enter a valid email address")
      isValid = false
    }
  
    // Organization validation
    if (!data.organization || data.organization.trim().length < 2) {
      showFieldError("organization", "Please enter your organization name")
      isValid = false
    }
  
    // Message validation
    if (!data.message || data.message.trim().length < 10) {
      showFieldError("message", "Please provide a detailed message (minimum 10 characters)")
      isValid = false
    }
  
    return isValid
  }
  
  function validateFormField(e) {
    const field = e.target
    const value = field.value.trim()
  
    clearFieldError(field.name)
  
    switch (field.name) {
      case "name":
        if (value.length < 2) {
          showFieldError("name", "Name must be at least 2 characters")
        }
        break
      case "email":
        if (!isValidEmail(value)) {
          showFieldError("email", "Please enter a valid email address")
        }
        break
      case "organization":
        if (value.length < 2) {
          showFieldError("organization", "Organization name is required")
        }
        break
      case "message":
        if (value.length < 10) {
          showFieldError("message", "Message must be at least 10 characters")
        }
        break
    }
  }
  
  function showFieldError(fieldName, message) {
    const field = document.querySelector(`[name="${fieldName}"]`)
    const errorElement = document.getElementById(`${fieldName}Error`)
  
    if (field) {
      field.classList.add("error")
    }
  
    if (errorElement) {
      errorElement.textContent = message
      errorElement.style.display = "block"
    }
  }
  
  function clearFieldError(fieldName) {
    const field = document.querySelector(`[name="${fieldName}"]`)
    const errorElement = document.getElementById(`${fieldName}Error`)
  
    if (field) {
      field.classList.remove("error")
    }
  
    if (errorElement) {
      errorElement.style.display = "none"
    }
  }
  
  // Contact methods functionality
  function initializeContactMethods() {
    const contactMethods = document.querySelectorAll(".contact-method")
  
    contactMethods.forEach((method) => {
      method.addEventListener("click", handleContactMethodClick)
    })
  }
  
  function handleContactMethodClick(e) {
    const method = e.currentTarget
    const contactType = method.getAttribute("data-contact-type")
  
    // Add visual feedback
    method.style.transform = "scale(0.98)"
    setTimeout(() => {
      method.style.transform = "scale(1)"
    }, 150)
  
    // Handle different contact methods
    switch (contactType) {
      case "email":
        window.location.href = "mailto:support@mediscan-ai.com"
        break
      case "phone":
        window.location.href = "tel:+1-800-MEDISCAN"
        break
      case "emergency":
        handleEmergencyContact()
        break
      default:
        console.log(`Contact method: ${contactType}`)
    }
  }
  
  // Emergency contact functionality
  function initializeEmergencyContact() {
    const emergencyBtn = document.getElementById("emergencyContact")
  
    if (emergencyBtn) {
      emergencyBtn.addEventListener("click", handleEmergencyContact)
    }
  }
  
  function handleEmergencyContact() {
    const emergencyModal = document.createElement("div")
    emergencyModal.className = "emergency-modal"
    emergencyModal.innerHTML = `
          <div class="emergency-modal-content">
              <div class="emergency-header">
                  <i class="fas fa-exclamation-triangle"></i>
                  <h3>Emergency Medical Support</h3>
                  <button class="modal-close" onclick="closeEmergencyModal()">&times;</button>
              </div>
              <div class="emergency-body">
                  <p><strong>For immediate medical emergencies:</strong></p>
                  <div class="emergency-contacts">
                      <div class="emergency-contact-item">
                          <i class="fas fa-phone"></i>
                          <div>
                              <strong>Emergency Hotline</strong>
                              <p><a href="tel:911">911</a> (Life-threatening emergencies)</p>
                          </div>
                      </div>
                      <div class="emergency-contact-item">
                          <i class="fas fa-hospital"></i>
                          <div>
                              <strong>Medical Support</strong>
                              <p><a href="tel:+1-800-MEDISCAN">+1-800-MEDISCAN</a> (Technical support)</p>
                          </div>
                      </div>
                      <div class="emergency-contact-item">
                          <i class="fas fa-envelope"></i>
                          <div>
                              <strong>Urgent Email</strong>
                              <p><a href="mailto:urgent@mediscan-ai.com">urgent@mediscan-ai.com</a></p>
                          </div>
                      </div>
                  </div>
                  <div class="emergency-disclaimer">
                      <p><strong>Important:</strong> MediScan AI is a diagnostic support tool. For medical emergencies, always contact emergency services or your healthcare provider immediately.</p>
                  </div>
              </div>
          </div>
      `
  
    document.body.appendChild(emergencyModal)
    document.body.style.overflow = "hidden"
  
    // Animate modal in
    setTimeout(() => {
      emergencyModal.style.opacity = "1"
      emergencyModal.querySelector(".emergency-modal-content").style.transform = "scale(1)"
    }, 50)
  }
  
  function closeEmergencyModal() {
    const modal = document.querySelector(".emergency-modal")
    if (modal) {
      modal.style.opacity = "0"
      modal.querySelector(".emergency-modal-content").style.transform = "scale(0.9)"
      setTimeout(() => {
        document.body.removeChild(modal)
        document.body.style.overflow = "auto"
      }, 300)
    }
  }
  
  // Form validation utilities
  function initializeFormValidation() {
    const inputs = document.querySelectorAll("input, select, textarea")
  
    inputs.forEach((input) => {
      // Real-time validation
      input.addEventListener("blur", function () {
        validateField(this)
      })
  
      input.addEventListener("input", function () {
        clearFieldError(this)
      })
    })
  
    // Add character counter for message field
    const messageField = document.querySelector('textarea[name="message"]')
    if (messageField) {
      const counter = document.createElement("div")
      counter.className = "character-counter"
      counter.textContent = "0/500 characters"
      messageField.parentNode.appendChild(counter)
  
      messageField.addEventListener("input", function () {
        const length = this.value.length
        counter.textContent = `${length}/500 characters`
        counter.style.color = length > 450 ? "#dc2626" : "#6b7280"
      })
    }
  
    // Add inquiry type descriptions
    const inquirySelect = document.querySelector('select[name="inquiry_type"]')
    if (inquirySelect) {
      inquirySelect.addEventListener("change", function () {
        showInquiryTypeDescription(this.value)
      })
    }
  }
  
  function validateField(field) {
    const value = field.value.trim()
    const fieldName = field.name
    let isValid = true
    let errorMessage = ""
  
    // Required field validation
    if (field.hasAttribute("required") && !value) {
      isValid = false
      errorMessage = `${getFieldLabel(field)} is required.`
    }
  
    // Specific field validations
    switch (fieldName) {
      case "email":
        if (value && !isValidEmail(value)) {
          isValid = false
          errorMessage = "Please enter a valid email address."
        }
        break
      case "name":
        if (value && value.length < 2) {
          isValid = false
          errorMessage = "Name must be at least 2 characters long."
        }
        break
      case "message":
        if (value && value.length < 10) {
          isValid = false
          errorMessage = "Message must be at least 10 characters long."
        }
        break
    }
  
    if (!isValid) {
      showFieldError(field, errorMessage)
    } else {
      clearFieldError(field)
    }
  
    return isValid
  }
  
  function showInquiryTypeDescription(inquiryType) {
    const descriptions = {
      technical: "Estimated response time: 4-8 hours during business days",
      clinical: "Estimated response time: 24-48 hours, reviewed by medical professionals",
      partnership: "Estimated response time: 2-3 business days, handled by business development",
      research: "Estimated response time: 3-5 business days, reviewed by research team",
      other: "Estimated response time: 24-48 hours",
    }
  
    const descriptionElement = document.getElementById("inquiryDescription")
    if (descriptionElement && descriptions[inquiryType]) {
      descriptionElement.textContent = descriptions[inquiryType]
      descriptionElement.style.display = "block"
    }
  }
  
  // Hover effects and animations
  function initializeHoverEffects() {
    const contactCards = document.querySelectorAll(".contact-method, .resource-card")
  
    contactCards.forEach((card) => {
      card.addEventListener("mouseenter", function () {
        this.style.transform = "translateY(-4px)"
        this.style.boxShadow = "var(--shadow-xl)"
      })
  
      card.addEventListener("mouseleave", function () {
        this.style.transform = "translateY(0)"
        this.style.boxShadow = "var(--shadow-md)"
      })
    })
  }
  
  // Utility functions
  function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return emailRegex.test(email)
  }
  
  function formatPhoneNumber(phone) {
    const cleaned = phone.replace(/\D/g, "")
    const match = cleaned.match(/^(\d{3})(\d{3})(\d{4})$/)
    if (match) {
      return `(${match[1]}) ${match[2]}-${match[3]}`
    }
    return phone
  }
  
  function validateOrganization(org) {
    const medicalOrganizations = [
      "hospital",
      "clinic",
      "medical center",
      "healthcare",
      "university",
      "research",
      "laboratory",
      "radiology",
    ]
  
    return medicalOrganizations.some((keyword) => org.toLowerCase().includes(keyword))
  }
  
  function getInquiryTypeDescription(type) {
    const descriptions = {
      technical: "Estimated response time: 4-8 hours during business days",
      clinical: "Estimated response time: 24-48 hours, reviewed by medical professionals",
      partnership: "Estimated response time: 2-3 business days, handled by business development",
      research: "Estimated response time: 3-5 business days, reviewed by research team",
      other: "Estimated response time: 24-48 hours",
    }
  
    return descriptions[type] || descriptions.other
  }
  
  function logMedicalInquiry(data) {
    // Log inquiry for medical professionals (in production, this would go to a database)
    const inquiryLog = {
      timestamp: new Date().toISOString(),
      type: "medical_inquiry",
      data: {
        name: data.name,
        organization: data.organization,
        inquiryType: data.inquiryType,
        urgent: data.urgent,
        messageLength: data.message.length,
      },
      responseTime: getInquiryTypeDescription(data.inquiryType),
    }
  
    console.log("Medical Inquiry Logged:", inquiryLog)
  }
  
  function setLoadingState(button, isLoading) {
    if (button) {
      button.disabled = isLoading
      if (isLoading) {
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...'
        button.classList.add("btn-loading")
      } else {
        button.innerHTML = '<i class="fas fa-paper-plane"></i> Send Message'
        button.classList.remove("btn-loading")
      }
    }
  }
  
  function showNotification(message, type) {
    const notification = document.createElement("div")
    notification.className = `notification ${type}`
    notification.innerHTML = `
          <div class="notification-content">
              <i class="fas fa-${type === "success" ? "check-circle" : "exclamation-triangle"}"></i>
              <span>${message}</span>
          </div>
          <button class="notification-close" onclick="this.parentElement.remove()">
              <i class="fas fa-times"></i>
          </button>
      `
  
    notification.style.cssText = `
          position: fixed;
          top: 90px;
          right: 20px;
          background: white;
          border: 1px solid var(--gray-200);
          border-left: 4px solid ${type === "success" ? "var(--success-green)" : "var(--error-red)"};
          border-radius: var(--radius-lg);
          padding: 1rem 1.5rem;
          box-shadow: var(--shadow-lg);
          z-index: 9999;
          transform: translateX(100%);
          transition: transform 0.3s ease;
          max-width: 400px;
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 1rem;
      `
  
    document.body.appendChild(notification)
  
    setTimeout(() => {
      notification.style.transform = "translateX(0)"
    }, 100)
  
    setTimeout(() => {
      if (document.body.contains(notification)) {
        notification.style.transform = "translateX(100%)"
        setTimeout(() => {
          if (document.body.contains(notification)) {
            document.body.removeChild(notification)
          }
        }, 300)
      }
    }, 5000)
  }
  
  // Export functions for external use
  window.ContactSystem = {
    initializeContactPage: initializeContactPage,
    handleEmergencyContact: handleEmergencyContact,
    validateContactForm: validateContactForm,
    formatPhoneNumber: formatPhoneNumber,
  }
  
  // Add emergency modal styles
  const emergencyStyles = document.createElement("style")
  emergencyStyles.textContent = `
      .emergency-modal {
          position: fixed;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          background: rgba(0, 0, 0, 0.5);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 10000;
          opacity: 0;
          transition: opacity 0.3s ease;
      }
      
      .emergency-modal-content {
          background: white;
          border-radius: var(--radius-xl);
          max-width: 500px;
          width: 90%;
          max-height: 80vh;
          overflow-y: auto;
          transform: scale(0.9);
          transition: transform 0.3s ease;
      }
      
      .emergency-header {
          display: flex;
          align-items: center;
          gap: 1rem;
          padding: 1.5rem;
          border-bottom: 1px solid var(--gray-200);
          background: #fef2f2;
          border-radius: var(--radius-xl) var(--radius-xl) 0 0;
      }
      
      .emergency-header i {
          color: var(--error-red);
          font-size: 1.5rem;
      }
      
      .emergency-header h3 {
          flex: 1;
          margin: 0;
          color: var(--error-red);
      }
      
      .modal-close {
          background: none;
          border: none;
          font-size: 1.5rem;
          color: var(--gray-500);
          cursor: pointer;
          padding: 0.5rem;
          border-radius: 50%;
          transition: all 0.2s ease;
      }
      
      .modal-close:hover {
          background: var(--gray-100);
          color: var(--gray-700);
      }
      
      .emergency-body {
          padding: 1.5rem;
      }
      
      .emergency-contacts {
          margin: 1rem 0;
      }
      
      .emergency-contact-item {
          display: flex;
          align-items: center;
          gap: 1rem;
          padding: 1rem;
          margin-bottom: 0.5rem;
          background: var(--gray-50);
          border-radius: var(--radius-lg);
      }
      
      .emergency-contact-item i {
          color: var(--error-red);
          font-size: 1.25rem;
          width: 20px;
          text-align: center;
      }
      
      .emergency-contact-item strong {
          display: block;
          color: var(--gray-900);
          margin-bottom: 0.25rem;
      }
      
      .emergency-contact-item p {
          margin: 0;
          color: var(--gray-600);
      }
      
      .emergency-contact-item a {
          color: var(--primary-blue);
          text-decoration: none;
          font-weight: 500;
      }
      
      .emergency-contact-item a:hover {
          text-decoration: underline;
      }
      
      .emergency-disclaimer {
          margin-top: 1.5rem;
          padding: 1rem;
          background: #fef3cd;
          border: 1px solid #fbbf24;
          border-radius: var(--radius-lg);
      }
      
      .emergency-disclaimer p {
          margin: 0;
          color: var(--gray-700);
          font-size: var(--font-size-sm);
      }
      
      .character-counter {
          font-size: var(--font-size-xs);
          color: var(--gray-500);
          text-align: right;
          margin-top: 0.25rem;
      }
      
      .form-group input.error,
      .form-group select.error,
      .form-group textarea.error {
          border-color: var(--error-red);
          box-shadow: 0 0 0 3px rgba(220, 38, 38, 0.1);
      }
      
      .field-error {
          color: var(--error-red);
          font-size: var(--font-size-sm);
          margin-top: 0.25rem;
          display: none;
      }
      
      .notification-content {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          flex: 1;
      }
      
      .notification-close {
          background: none;
          border: none;
          color: var(--gray-500);
          cursor: pointer;
          padding: 0.25rem;
          border-radius: 50%;
          transition: all 0.2s ease;
      }
      
      .notification-close:hover {
          background: var(--gray-100);
          color: var(--gray-700);
      }
  `
  
  document.head.appendChild(emergencyStyles)
  
  function getFieldLabel(field) {
    const label = field.closest(".form-group")?.querySelector("label")
    return label ? label.textContent.replace("*", "").trim() : field.name
  }
  
  // Auto-fill functionality for returning users
  function initializeAutoFill() {
    const savedData = localStorage.getItem("mediscan_contact_data")
    if (savedData) {
      try {
        const data = JSON.parse(savedData)
        const form = document.getElementById("contactForm")
  
        Object.keys(data).forEach((key) => {
          const field = form.querySelector(`[name="${key}"]`)
          if (field && field.type !== "checkbox") {
            field.value = data[key]
          }
        })
      } catch (error) {
        console.error("Error loading saved contact data:", error)
      }
    }
  }
  
  // Save form data for convenience
  function saveFormData() {
    const form = document.getElementById("contactForm")
    const formData = new FormData(form)
    const data = {}
  
    // Save non-sensitive data only
    const fieldsToSave = ["name", "organization", "inquiry_type"]
    fieldsToSave.forEach((field) => {
      if (formData.has(field)) {
        data[field] = formData.get(field)
      }
    })
  
    localStorage.setItem("mediscan_contact_data", JSON.stringify(data))
  }