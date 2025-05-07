# Fix CommBank OFX

CommBank produces non-conformant OFX files by omitting the FITID field
for Credit Interest transactions. This prevents the files from being
imported by spec-conformant software such as ofxtools or Zoho Books.

This script fixes the non-conformant CommBank OFX files by replacing the
missing FITID field values with the transaction date and the memo value.
Because credit interest is only paid monthly, this is sufficient to
ensure that the replacement FITID field is a valid unique identifier
which can be used for its intended purpose of identifying duplicate
transactions when importing statements.

## Usage

After installing the package, run the script as follows:

    fix-commbank-ofx path/to/file.ofx

This will create a fixed file at:

    path/to/file-fixed.ofx
