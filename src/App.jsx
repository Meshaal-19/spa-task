import { BrowserRouter, Routes, Route, Link, Outlet } from "react-router-dom";
import { useState } from "react";
import "./App.css";

function Layout() {
  return (
    <>
      <nav className="navbar">
        <h2>My SPA</h2>

        <div>
          <Link to="/">Home</Link>
          <Link to="/about">About</Link>
          <Link to="/contact">Contact</Link>
        </div>
      </nav>

      <main className="container">
        <Outlet />
      </main>
    </>
  );
}

function Home() {
  return <h1>Home Page</h1>;
}

function About() {
  return <h1>About Page</h1>;
}

function Contact() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [errors, setErrors] = useState({});

  function handleSubmit(e) {
    e.preventDefault();

    const newErrors = {};

    if (!name.trim()) {
      newErrors.name = "Name is required";
    }

    if (!email.trim()) {
      newErrors.email = "Email is required";
    } else if (!email.includes("@")) {
      newErrors.email = "Invalid email address";
    }

    if (!message.trim()) {
      newErrors.message = "Message is required";
    }

    setErrors(newErrors);

    if (Object.keys(newErrors).length === 0) {
      alert("Form submitted successfully!");

      setName("");
      setEmail("");
      setMessage("");
      setErrors({});
    }
  }

  return (
    <>
      <h1>Contact Us</h1>

      <form onSubmit={handleSubmit}>
        <div>
          <input
            type="text"
            placeholder="Name"
            value={name}
            onChange={(e) => {
              setName(e.target.value);
              setErrors((prev) => ({ ...prev, name: "" }));
            }}
          />
          <p>{errors.name}</p>
        </div>

        <div>
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => {
              setEmail(e.target.value);
              setErrors((prev) => ({ ...prev, email: "" }));
            }}
          />
          <p>{errors.email}</p>
        </div>

        <div>
          <textarea
            placeholder="Message"
            value={message}
            onChange={(e) => {
              setMessage(e.target.value);
              setErrors((prev) => ({ ...prev, message: "" }));
            }}
          />
          <p>{errors.message}</p>
        </div>

        <button type="submit">Submit</button>
      </form>
    </>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Home />} />
          <Route path="/about" element={<About />} />
          <Route path="/contact" element={<Contact />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;