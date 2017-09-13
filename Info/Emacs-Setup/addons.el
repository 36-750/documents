;;; -*- mode: emacs-lisp; lexical-binding: t; -*-

(eval-when-compile
  (require 'use-package))
(setq use-package-verbose t)

(use-package s
  :config (defun s-str (obj) (format "%s" obj)))
(use-package dash)
(use-package f
  :config (defalias 'f-slash* 'file-name-as-directory))
(use-package ht)
(use-package bind-key)
(use-package diminish)
(use-package hydra)
(use-package pallet)  ; use pallet and cask to keep up-to-date package list

(use-package ess)
