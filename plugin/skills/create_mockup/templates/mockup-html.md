# mockup.html

Step 6 — `mockups/v00N/mockup.html`. Every class must come from research; no placeholders.

`````html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Mockup: [Feature Name] v001</title>

  <!-- Import app's styles based on research -->
  <!-- If using Tailwind: -->
  <script src="https://cdn.tailwindcss.com"></script>

  <!-- If using app's CSS files (adjust paths): -->
  <!-- <link rel="stylesheet" href="../../src/styles/main.css"> -->

  <!-- If using icon library from research: -->
  <!-- Font Awesome example: -->
  <!-- <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"> -->

  <!-- Material Icons example: -->
  <!-- <link rel="stylesheet" href="https://fonts.googleapis.com/icon?family=Material+Icons"> -->

  <style>
    /* Add any custom styles needed to match app exactly */
    /* Copy from discovered theme/color tokens */
  </style>
</head>
<body class="[discovered body classes from research]">

  <!-- Header/Navigation - copy structure from research file:line -->
  <header class="[actual header classes from app]">
    <!-- Use actual nav structure from research -->
  </header>

  <!-- Main content area -->
  <main class="[layout classes from research]">

    <!-- Feature mockup using real component HTML -->
    <div class="[container classes from research]">

      <h1 class="[heading classes from research]">
        <!-- Icon if system found: -->
        <!-- <i class="fa-solid fa-[icon-name]"></i> -->
        [Feature Title]
      </h1>

      <!-- Content sections matching ASCII diagram -->

      <!-- Buttons using app's actual button HTML -->
      <div class="[button container classes]">
        <button class="[primary button classes from research]">
          <!-- Icon if used in app: -->
          <!-- <i class="fa-solid fa-save"></i> -->
          Primary Action
        </button>
        <button class="[secondary button classes from research]">
          Secondary Action
        </button>
      </div>

    </div>

  </main>

  <!-- Footer if app has one -->

</body>
</html>
`````
