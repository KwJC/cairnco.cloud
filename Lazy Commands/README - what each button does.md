# Lazy Commands

Six buttons. Double-click one. Each explains itself and asks before doing
anything permanent.

They all run against the folder **above** this one, which is the website. Do not
move them out of here on their own; they find the site by their own location.

## The two you will use most

### BUILD-AND-DEPLOY.bat
Turns `src\` into finished pages, checks ten key files came out, then asks
before publishing to the live site. Answer **N** at the publish question and it
builds without touching anything public, which is what you want before a
preview.

### PREVIEW.bat
Shows you the built site on this computer at **http://localhost:8000**, exactly
as Cloudflare will serve it. Opens a second window that does the serving. Close
that window when you are done.

Run BUILD-AND-DEPLOY first, or there is nothing to preview.

> **Why not just double-click `dist\index.html`?** Every link in the site starts
> with `/`, meaning "the top of the site". A browser reading off your disk has no
> site, so it reads `/` as the top of your C: drive. The home page paints and
> every single link is dead. This button is the fix.

## Sending work back and forth

These two go in **opposite directions**. That is the only thing you need to
remember about them.

### SAVE-TO-GITHUB.bat
**Upload.** Your work goes up to GitHub so it is backed up and Emmanuel can see
it. Shows you what is about to be saved and asks you to describe it.

If GitHub refuses, it means Emmanuel saved something first. Run PULL-LATEST,
then run this again.

### PULL-LATEST.bat
**Download.** Emmanuel's work comes down to your computer.

It refuses to run if you have unsaved work, and tells you to save first. It can
never destroy anything you have not backed up.

If it says your histories have split, that means you and Emmanuel both have work
the other does not. Stop and tell Claude. Do not force it.

## One-offs

### MERGE-EMMANUEL-AND-SAVE.bat
Written for one specific day: 22 Sep 2026, when you and Emmanuel both changed
the site at the same time and Claude combined the two by hand. Run it once, then
delete it. It will not be correct for any other situation.

### DELETE-OLD-FILES.bat
Already did its job. Run it once more and it removes itself.

## If something goes wrong

Every button stops at the first sign of trouble and changes nothing further.
Copy the message on screen and send it to Claude. None of them will leave you
half-finished.
