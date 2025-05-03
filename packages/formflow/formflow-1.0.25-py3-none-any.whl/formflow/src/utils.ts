export function copyToClipboard(element: HTMLElement): void {
  // Get the previous sibling, which is the <pre> element containing the <code>
  const preElement = element.previousElementSibling as HTMLElement;
  const codeElement = preElement.querySelector('code') as HTMLElement;

  if (codeElement) {
    const text = codeElement.textContent || '';

    // Copy text to clipboard
    navigator.clipboard.writeText(text).then(() => {
      // Get the next sibling, which is the tooltip div
      const tooltip = element.nextElementSibling as HTMLElement;

      if (tooltip) {
        tooltip.textContent = 'Copied to clipboard!';
        tooltip.style.opacity = '1';

        // Hide the tooltip after 3 seconds
        setTimeout(() => {
          tooltip.style.opacity = '0';
        }, 3000);
      }
    }).catch((err) => {
      alert(`Failed to copy text: ${err}`);
    });
  }
}

export function formToJson(form: any) {
    // Create a FormData object from the form
    const formData = new FormData(form);
    // Convert the FormData object to a plain object
    const formObject: any = {};
    formData.forEach((value, key) => {
        formObject[key] = value;
    });
    // Convert the form object to JSON
    return JSON.stringify(formObject);
}
