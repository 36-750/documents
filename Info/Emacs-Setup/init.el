;;; -*- mode: emacs-lisp; lexical-binding: t; -*-

(require 'package)
(package-initialize)

(setq package-enable-at-startup t
      package-archives '(("gnu" . "http://elpa.gnu.org/packages/")
                         ("melpa" . "http://melpa.org/packages/")
                         ("melpa-stable" . "http://stable.melpa.org/packages/")
                         ("org" . "http://orgmode.org/elpa/")))

(require 'cl-lib)

(defconst my-platform
  (cond ((or (string-equal system-type "darwin")
             (eq window-system 'ns)
             (eq window-system 'mac))
	 'macosx)
	((or (string-equal system-type "ms-dos")
             (string-equal system-type "windows-nt")
	     (string-equal system-type "cygwin"))
	 'windows)
        (t
         'linux))
  "The platform on which we are currently running, derived from
the variables `system-type' and `window-system'. Value is a
symbol. For the moment, all *nix variants are converted to
`linux', though this can be generalized later if needed")


;;; Operational Settings

(setq ;inhibit-startup-message   t
      load-prefer-newer         t
      visible-bell              t
      initial-major-mode        'fundamental-mode
      indent-tabs-mode          nil
      scroll-error-top-bottom   t
      switch-to-visible-buffer  nil
      kill-read-only-ok         t
      indicate-empty-lines      t
      require-final-newline     t)

(setq history-length 512)
(setq paragraph-start paragraph-separate            ; Use blank lines to separate paragraphs by default
      adaptive-fill-regexp "[ \t]*\\([>*%#]+ +\\)?" ; Fill around comment beginnings and yanked-messages
      sentence-end-double-space nil                 ; Allow frenchspacing
      page-delimiter "^\\(\f\\|\n\n+\\)")           ; FF or 2+ consecutive blank lines
(setq print-length 1024                 ; Give more information about objects in help
      print-level  8
      eval-expression-print-length 1024 
      eval-expression-print-level  8)

(setq-default indent-tabs-mode nil)

(dolist (s '(tool-bar-mode scroll-bar-mode horizontal-scroll-bar-mode))
  (if (fboundp s) (funcall s -1)))

(dolist (s '(eval-expression narrow-to-region narrow-to-page scroll-left
              downcase-region upcase-region set-goal-column))
  (put s 'disabled nil))


;;; System-Specific Settings

(when window-system
  (setq frame-title-format '("" invocation-name " <%b>"))
  (mouse-wheel-mode  1)
  (blink-cursor-mode 1))

(when (eq my-platform 'macosx)
  (setq ns-command-modifier  'meta) 
  (setq ns-option-modifier   'alt)
  (setq ns-function-modifier 'super)

  (define-key key-translation-map     [s-mouse-1]          [mouse-2])
  (define-key key-translation-map   [C-s-mouse-1]        [C-mouse-2])
  (define-key key-translation-map   [M-s-mouse-1]      [M-C-mouse-2])

  (define-key key-translation-map   [s-S-mouse-1]     [down-mouse-2])
  (define-key key-translation-map [C-s-S-mouse-1]   [C-down-mouse-2])
  (define-key key-translation-map [M-s-S-mouse-1] [M-C-down-mouse-2])

  (define-key key-translation-map     [A-mouse-1]          [mouse-3])
  (define-key key-translation-map   [C-A-mouse-1]        [C-mouse-3])
  (define-key key-translation-map   [M-A-mouse-1]      [M-C-mouse-3])

  (define-key key-translation-map   [A-S-mouse-1]     [down-mouse-3])
  (define-key key-translation-map [C-A-S-mouse-1]   [C-down-mouse-3])
  (define-key key-translation-map [M-A-S-mouse-1] [M-C-down-mouse-3]))


;;; Basic Utilities

(require 'uniquify)
(setq uniquify-buffer-name-style 'post-forward 
      uniquify-separator " in "
      uniquify-after-kill-buffer-p t)

(require 'saveplace)
(setq-default save-place t)
(setq save-place-file (concat user-emacs-directory "places"))


;;; Keybindings

(cl-macrolet ((by-five (cmd)            ; Move more quickly
                       `(lambda ()
                          (interactive)
                          (ignore-errors (,cmd 5)))))
  (bind-key "C-S-n" (by-five next-line))
  (bind-key "C-S-p" (by-five previous-line))
  (bind-key "C-S-f" (by-five forward-char))
  (bind-key "C-S-b" (by-five backward-char))
  (bind-key [(meta shift ?f)] (by-five forward-word))
  (bind-key [(meta shift ?b)] (by-five backward-word)))

(global-set-key (kbd "M-/") 'hippie-expand)
(global-set-key (kbd "C-x C-b") 'ibuffer)
(global-set-key (kbd "C-z") 'zap-up-to-char)

(global-set-key "\C-x\C-m"    'execute-extended-command)


;;; Initial State

(auto-compression-mode '1)               ; Auto view compressed files
(transient-mark-mode '1)                 ; Highlight region
(show-paren-mode '1)                     ; show matching parens


(server-start)  ; allow emacsclient to connect, e.g., in git
