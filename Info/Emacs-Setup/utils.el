;;; -*- mode: emacs-lisp; lexical-binding: t; -*-

;;; Convenience Utilities

(defun my/move-beginning-of-line (&optional n)
  "Move to beginning of N-1st line ahead or to first non-whitespace character.
If not at the beginning of a line, move point to the beginning of the line,
moving forward n - 1 lines first if n is not nil or 1.
If at the beginning of a line, move instead back to the first
non-whitespace character on that line, ignoring N."
  (interactive "p")
  (if (looking-at "^")
      (back-to-indentation)
    (move-beginning-of-line n)))

(defun start-shell (&optional dir buffer)
  (interactive "DWorking directory: \nBShell buffer name: ")
  (let ((default-directory (or (file-name-as-directory dir) default-directory)))
    (shell buffer)))

(defun with-infinite-fill (func)
  "Set effectively infinite fill column during function FUNC.
FUNC should be a symbol with non-void, interactive function
definition. Inspired by `ourcomments-util' and Sean Burke."
  (let ((fill-column most-positive-fixnum))
    (call-interactively func)))

(defun unfill-paragraph ()
  "Convert a paragraph a single line of text."
  (interactive)
  (with-infinite-fill 'fill-paragraph))

(defun unfill-region ()
  "Convert all paragraphs in the region into
single lines of text."
  (interactive)
  (with-infinite-fill 'fill-region))

(defun unfill-individual-paragraphs ()
  "Convert each paragraph in the region into
single lines of text, respecting each individual
paragraph's indentation and (apparent) fill prefix."
  (interactive)
  (with-infinite-fill 'fill-individual-paragraphs))

(defvar my/cua-rectangle-key [(control ?c) (control return)])
(defun enable-cua-rectangles ()
  "Turn on (only) the rectangle feature of cua mode.
Also, take care of conflicting keybindings with icicles. Should
be called before `my-set-completion-mode' in
`my-set-operating-state' so that icicles properly sets up its
bindings. But if called manually, then icy-mode should be cycled
on and off afterwards."
  (interactive)
  (cond
   ((and (boundp 'cua-rectangle-mark-key)
         (memq 'standard-value (symbol-plist 'cua-rectangle-mark-key))
         (bound-and-true-p my/cua-rectangle-key))
    (customize-set-variable 'cua-rectangle-mark-key my/cua-rectangle-key))
   ((bound-and-true-p my/cua-rectangle-key)
    (setq cua-rectangle-mark-key my/cua-rectangle-key)))
  (setq cua-enable-cua-keys nil)
  (require-soft 'cua-rect)
  (eval-after-load 'cua-rect
    (progn
      (cua-mode t)
      (cua--rect-M/H-key ?\ 'cua-close-rectangle)
      (cua--rect-M/H-key ?c 'cua-copy-rectangle)
      (message "In cua rectangle now M-<space>: close, M-c: copy")))
  (delete-selection-mode -1))

(defun keyboard-escape-quit ()
  "Exit the current \"mode\" (in a generalized sense of the word).
This command can exit an interactive command such as
`query-replace', can clear out a prefix argument or a region, can
get out of the minibuffer or other recursive edit, cancel the use
of the current buffer (for special-purpose buffers)."
  (interactive)
  (cond ((eq last-command 'mode-exited) nil)
        ((region-active-p)
         (deactivate-mark))
        ((> (minibuffer-depth) 0)
         (abort-recursive-edit))
        (current-prefix-arg
         nil)
        ((> (recursion-depth) 0)
         (exit-recursive-edit))
        (buffer-quit-function
         (funcall buffer-quit-function))
        ((string-match "^ \\*" (buffer-name (current-buffer)))
         (bury-buffer))))

(defun make-backup-file-name (file)
  "Create the non-numeric backup file name for FILE.
This is a separate function so you can redefine it for customization."
  (concat (file-name-directory file)
          (concat "." (concat (file-name-nondirectory file) "~"))))

;;ATTN: need to redefine `backup-file-name-p' and `file-name-sans-version' also
;; to be consistent with the above definition!
;; Note also the variable `make-backup-file-name-function'
;; which can be used instead of wholesale redefining make-backup-file-name
;; but since I have to redefine two others, might as well redefine all three

(defun backup-file-name-p (file)
  "Return non-nil if FILE is a backup file name (numeric or not).
This is a separate function so you can redefine it for customization.
You may need to redefine `file-name-sans-versions' as well."
    (string-match "\\`\\..*~\\'" file))

(defvar file-name-version-regexp
  "\\(?:~\\|\\.~[-[:alnum:]:#@^._]+\\(?:~[[:digit:]]+\\)?~\\)"
  ;; The last ~[[:digit]]+ matches relative versions in git,
  ;; e.g. `foo.js.~HEAD~1~'.
  "Regular expression matching the backup/version part of a file name.
Used by `file-name-sans-versions'.")

;; ATTN this is not updated yet
(defun file-name-sans-versions (name &optional keep-backup-version)
  "Return file NAME sans backup versions or strings.
This is a separate procedure so your site-init or startup file can
redefine it.
If the optional argument KEEP-BACKUP-VERSION is non-nil,
we do not remove backup version numbers, only true file version numbers.
See also `file-name-version-regexp'."
  (let ((handler (find-file-name-handler name 'file-name-sans-versions)))
    (if handler
	(funcall handler 'file-name-sans-versions name keep-backup-version)
      (substring name 0
		 (unless keep-backup-version
                   (string-match (concat file-name-version-regexp "\\'")
                                 name))))))


;;; Use the utilities

(global-set-key "\C-a"        'my/move-beginning-of-line)
(enable-cua-rectangles)

