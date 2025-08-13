// Result page JavaScript functionality

document.addEventListener("DOMContentLoaded", () => {
  initializeConfidenceAnimation()
  initializeImageModal()
  initializePrintDownload()
  initializeResultAnimations()
  initializeAccessibility()
  console.log("Medical analysis results interface initialized")
})

function initializeConfidenceAnimation() {
  const confidenceFill = document.querySelector(".confidence-fill")
  if (confidenceFill) {
    const targetWidth = confidenceFill.style.width
    confidenceFill.style.width = "0%"

    setTimeout(() => {
      confidenceFill.style.width = targetWidth
    }, 1000)
  }
}

function initializeImageModal() {
  const medicalImage = document.getElementById("medicalImage")
  const imageModal = document.getElementById("imageModal")
  const modalImage = document.getElementById("modalImage")

  if (medicalImage && imageModal && modalImage) {
    medicalImage.addEventListener("click", () => {
      openImageModal()
    })
  }
}

function openImageModal() {
  const medicalImage = document.getElementById("medicalImage")
  const imageModal = document.getElementById("imageModal")
  const modalImage = document.getElementById("modalImage")

  if (medicalImage && imageModal && modalImage) {
    modalImage.src = medicalImage.src
    imageModal.style.display = "block"
    document.body.style.overflow = "hidden"
  }
}

function closeImageModal() {
  const imageModal = document.getElementById("imageModal")
  if (imageModal) {
    imageModal.style.display = "none"
    document.body.style.overflow = "auto"
  }
}

function initializePrintDownload() {
  // Print functionality
  window.print = () => {
    const printWindow = window.open("", "_blank")
    const printContent = generatePrintContent()

    printWindow.document.write(printContent)
    printWindow.document.close()
    printWindow.print()
    printWindow.close()
  }
}

function downloadReport() {
  // Create a comprehensive report
  const reportData = gatherReportData()
  const reportContent = generateReportContent(reportData)

  // Create and download PDF (simplified version)
  const element = document.createElement("a")
  const file = new Blob([reportContent], { type: "text/html" })
  element.href = URL.createObjectURL(file)
  element.download = `MediScan_AI_Report_${new Date().toISOString().split("T")[0]}.html`
  document.body.appendChild(element)
  element.click()
  document.body.removeChild(element)

  showNotification("Report downloaded successfully", "success")
}

function gatherReportData() {
  const conditionValue = document.querySelector(".condition-value")
  const confidenceValue = document.querySelector(".confidence-value")
  const timestamp = document.querySelector(".meta-item span")
  const recommendations = document.querySelectorAll(".recommendations-list li span")

  return {
    condition: conditionValue?.textContent || "Unknown",
    confidence: confidenceValue?.textContent || "0%",
    timestamp: timestamp?.textContent || new Date().toLocaleString(),
    recommendations: Array.from(recommendations).map((r) => r.textContent),
    analysisId: `MSA-${Date.now()}`,
  }
}

function generateReportContent(data) {
  return `
    <!DOCTYPE html>
    <html>
    <head>
      <title>MediScan AI Analysis Report</title>
      <style>
        body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; color: #333; }
        .header { text-align: center; margin-bottom: 30px; border-bottom: 2px solid #2563eb; padding-bottom: 20px; }
        .logo { color: #2563eb; font-size: 24px; font-weight: bold; }
        .result-summary { background: #f8fafc; padding: 20px; border-radius: 8px; margin: 20px 0; }
        .condition { font-size: 18px; font-weight: bold; color: #1e293b; }
        .confidence { color: #2563eb; font-weight: bold; }
        .recommendations { margin: 20px 0; }
        .recommendations li { margin: 10px 0; }
        .disclaimer { background: #fef3c7; padding: 15px; border-radius: 8px; margin-top: 30px; font-size: 12px; }
      </style>
    </head>
    <body>
      <div class="header">
        <div class="logo">🔬 MediScan AI</div>
        <h1>Medical Image Analysis Report</h1>
        <p>Analysis ID: ${data.analysisId}</p>
        <p>Generated: ${data.timestamp}</p>
      </div>
      
      <div class="result-summary">
        <h2>Analysis Results</h2>
        <p><strong>Detected Condition:</strong> <span class="condition">${data.condition}</span></p>
        <p><strong>Confidence Level:</strong> <span class="confidence">${data.confidence}</span></p>
      </div>
      
      <div class="recommendations">
        <h2>Clinical Recommendations</h2>
        <ul>
          ${data.recommendations.map((rec) => <li>${rec}</li>).join("")}
        </ul>
      </div>
      
      <div class="disclaimer">
        <strong>Medical Disclaimer:</strong> This AI analysis is for informational purposes only and should not replace professional medical advice. Always consult with qualified healthcare providers.
      </div>
    </body>
    </html>
  `
}

function generatePrintContent() {
  const reportData = gatherReportData()
  return generateReportContent(reportData)
}

function initializeResultAnimations() {
  // Animate result cards on load
  const resultCards = document.querySelectorAll(".analysis-summary, .image-display, .recommendations-section")
  resultCards.forEach((card, index) => {
    card.style.opacity = "0"
    card.style.transform = "translateY(20px)"

    setTimeout(() => {
      card.style.transition = "all 0.6s ease"
      card.style.opacity = "1"
      card.style.transform = "translateY(0)"
    }, index * 200)
  })

  // Animate urgency badge
  const urgencyBadge = document.querySelector(".urgency-badge")
  if (urgencyBadge) {
    setTimeout(() => {
      urgencyBadge.style.animation = "pulse 2s infinite"
    }, 1500)
  }
}

function initializeAccessibility() {
  // Add keyboard navigation for image modal
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      closeImageModal()
    }

    if (e.key === "Enter" && e.target.classList.contains("medical-image")) {
      openImageModal()
    }
  })

  // Add ARIA labels
  const medicalImage = document.getElementById("medicalImage")
  if (medicalImage) {
    medicalImage.setAttribute("role", "button")
    medicalImage.setAttribute("tabindex", "0")
    medicalImage.setAttribute("aria-label", "Click to view full-size medical image")
  }

  // Add focus indicators
  const focusableElements = document.querySelectorAll("button, .medical-image, .btn")
  focusableElements.forEach((element) => {
    element.addEventListener("focus", () => {
      element.style.outline = "2px solid #2563eb"
      element.style.outlineOffset = "2px"
    })

    element.addEventListener("blur", () => {
      element.style.outline = "none"
    })
  })
}

// Modal event listeners
document.addEventListener("click", (e) => {
  const imageModal = document.getElementById("imageModal")
  if (e.target === imageModal) {
    closeImageModal()
  }
})

// Add CSS animations
const style = document.createElement("style")
style.textContent = `
  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.7; }
  }
  
  .medical-image {
    cursor: pointer;
    transition: transform 0.3s ease;
  }
  
  .medical-image:hover {
    transform: scale(1.02);
  }
  
  .image-modal {
    backdrop-filter: blur(5px);
  }
  
  .modal-content {
    animation: modalFadeIn 0.3s ease;
  }
  
  @keyframes modalFadeIn {
    from {
      opacity: 0;
      transform: scale(0.9);
    }
    to {
      opacity: 1;
      transform: scale(1);
    }
  }
`
document.head.appendChild(style)

// Export functions for external use
window.ResultSystem = {
  initializeConfidenceAnimation: initializeConfidenceAnimation,
  downloadReport: downloadReport,
  gatherReportData: gatherReportData,
  generateReportContent: generateReportContent,
}

function copyToClipboard(text) {
  const tempInput = document.createElement("input")
  tempInput.value = text
  document.body.appendChild(tempInput)
  tempInput.select()
  document.execCommand("copy")
  document.body.removeChild(tempInput)
}

function showNotification(message, type) {
  // Placeholder for notification function
  console.log(`Notification (${type}): ${message}`)
}

function showLoading(button) {
  button.disabled = true
  button.textContent = "Loading..."
}

function hideLoading(button) {
  button.disabled = false
  button.textContent = "Download Report"
}

function trapFocus(modal) {
  const focusableElements = modal.querySelectorAll(
    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])',
  )
  const firstFocusableElement = focusableElements[0]
  const lastFocusableElement = focusableElements[focusableElements.length - 1]

  modal.addEventListener("keydown", (e) => {
    const isTabPressed = e.key === "Tab" || e.keyCode === 9

    if (!isTabPressed) {
      return
    }

    if (e.shiftKey) {
      if (document.activeElement === firstFocusableElement) {
        lastFocusableElement.focus()
        e.preventDefault()
      }
    } else {
      if (document.activeElement === lastFocusableElement) {
        firstFocusableElement.focus()
        e.preventDefault()
      }
    }
  })

  firstFocusableElement.focus()
}

// Add print styles dynamically
const printStyles = `
    @media print {
        .navbar, .footer, .action-buttons, .image-zoom-btn {
            display: none !important;
        }
        .main-content {
            margin-top: 0 !important;
        }
        .results-container {
            grid-template-columns: 1fr !important;
        }
        .medical-image {
            max-width: 300px !important;
            height: auto !important;
        }
        body {
            font-size: 12pt !important;
            line-height: 1.4 !important;
            color: #000 !important;
        }
        .analysis-summary, .recommendations-section {
            break-inside: avoid !important;
            margin-bottom: 20px !important;
        }
    }
`

const styleSheet = document.createElement("style")
styleSheet.textContent = printStyles
document.head.appendChild(styleSheet)