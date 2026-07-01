export function validateForm(formData) {
  const errors = {};
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  if (!formData.name.trim()) {
    errors.name = "Name is required";
  }

  if (!formData.email.trim()) {
    errors.email = "Email is required";
  } else if (!emailRegex.test(formData.email)) {
    errors.email = "Invalid email address";
  }

  if (!formData.message.trim()) {
    errors.message = "Message is required";
  }

  return errors;
}
