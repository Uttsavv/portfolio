# Site content

Everything the page says comes from these files. Edit them and push; the site rebuilds.

- `profile.json`: name, role, stack, city, email, links (GitHub, LinkedIn, resume) and the SEO title/description.
  - `links.resume`: a path like `/resume.pdf` (put the file in `public/`) or a full URL. Empty hides the link.
  - `links.linkedin` / `email`: empty hides them.
  - `contactForm.endpoint`: optional form service URL (Formspree, Web3Forms, …) that accepts a JSON POST. Empty = the form opens the visitor's mail app.
- `experience.json`: newest job first. `end: null` means current. Each job gets a block in the 3D scene.
- `projects.json`: shown one at a time in order. `model` picks the 3D object: `handheld`, `kanban`, `jar` or `terminal`.

`placeholder: true` only marks entries that still need real content; it is never shown.
