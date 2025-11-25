library(testthat)
library(stringr)
library(rlang)
library(purrr)

source("parse_quotes.r")

#
# Tests
#

test_that("simple quoted strings", {
    expect_equal( parse_quoted('""'), "" )
    expect_equal( parse_quoted('"abc"'), "abc" )
    expect_equal( parse_quoted('"abc\\ndef"'), "abc\ndef" )
    expect_equal( parse_quoted('"abc\\\"def"'), "abc\"def" )
    expect_equal( parse_quoted('"abc\\\\\\\\ndef"'), "abc\\\\ndef" )
    expect_equal( parse_quoted('"abc\\\\\\\\\\nxyz"'), "abc\\\\\nxyz" )

    expect_error( parse_quoted('"abc\\ndef'), "Expected character \"")
})
