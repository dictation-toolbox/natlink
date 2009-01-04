# dvc2vcl.pl - convert dragon voice commands to Vocola commands
#
# Usage: perl dvc2vcl.pl [input_folder] [output_folder]
#
# Converts each .dvc file in input_folder to one or more .vcl files in
# output_folder.  Global commands are written to _Vocola.vcl;
# application-specific commands for application "foo" are written to
# foo.vcl
#
# This file is copyright (c) 2002-2003 by Rick Mohr. It may be redistributed 
# in any way as long as this copyright notice remains.

use Text::ParseWords;    # for quotewords

# ---------------------------------------------------------------------------
# Main control flow

$debug = 0;
&convert_folder;

sub convert_folder    # Convert each .dvc file to one or more .vcl files
{
    if (@ARGV == 0) {
        $in_folder = ".";
        $out_folder = ".";
    } elsif (@ARGV == 2) {
        $in_folder = $ARGV[0];
        $out_folder = $ARGV[1];
    } else {
        die "dvc2vcl: Requires 0 or 2 command line arguments\n";
    }

    opendir FOLDER, "$in_folder" or die "Couldn't open folder '$in_folder'\n";

    foreach (readdir FOLDER)
    {
        if (/^(.+)\.dvc$/) {
            $in_file = "$in_folder/$1.dvc";
            open IN, "<$in_file" or die "$@ $in_file";
            print "\nConverting $in_file\n";
            &convert_file;
            close IN;
        }
    }
}

sub convert_file
{
    $line_number = 0;
    while (<IN>) {
        $line_number++;
        next if /^\s*$/;
        if (/^\s*MENU\s*\"(.*?)\"\s*\{/) {
            $application = $1;
            $application = "_Vocola" if $application eq "Global Commands";
            close OUT if OUT;
            my $out_file = "$out_folder/$application.vcl";
            open OUT, ">$out_file" or die "$@ $out_file";
            $now = localtime;
            if ($application eq "_Vocola") {
                print OUT "\# Global voice commands\n";
            } else {
                print OUT "\# Voice commands for $application\n";
            }
            print OUT "\# Translated from $in_file\n";
            print OUT "\# Translated by dvc2vcl on ", $now, "\n\n";
            &parse_application;
        } else {
            die "Expected MENU\n";
        }
    }
    close OUT;
}

sub parse_application
{
    while (<IN>) {
        $line_number++;
        next if /^\s*$/;
        if (/^\s*STATE\s*\"(.*?)\".*?\{/) {
            $context = $1;
            $context = "" if $context eq "Global Commands";
            print OUT "$context:\n";
            &parse_definition;
        } elsif (/^\s*\}/) {
            return;
        } else {
            die "Expected STATE\n";
        }
    }
}

sub parse_definition
{
    while (<IN>) {
        $line_number++;
        next if /^\s*$/;
        if (/^\s*COMMAND\s*\"(.*?)\"\s*\{/) {
            $line = "$1 =";
            $trouble = 0;
            &parse_command;
            if ($trouble) {print OUT "# $line"}
            else          {print OUT "  $line"}
        } elsif (/^\s*LIST\s*\"(.*?)\"\s*\{/) {
            $line = "<$1> :=";
            $trouble = 0;
            &parse_list;
            if ($trouble) {print OUT "# $line"}
            else          {print OUT "  $line"}
        } elsif (/^\s*\}/) {
            print OUT "\n";
            return;
        } else {
            die "Expected COMMAND or LIST\n";
        }
    }
}

sub parse_command
{
    while (<IN>) {
        $line_number++;
        next if /^\s*$/;
        if (/^\s*SCRIPT\s*\"(.*?)\"/) {
            $line .= " []";
            $trouble = 1;
        } elsif (/^\s*SCRIPT\s*\{/) {
            &parse_script;
        } elsif (/^\s*KEYS\s*\{/) {
            &parse_keys;
        } elsif (/^\s*\}/) {
            $line .= ";\n";
            return;
        } else {
            die "Expected SCRIPT or KEYS\n";
        }
    }
}

sub parse_script
{
    while (<IN>) {
        $line_number++;
        next if /^\s*$/;
        next if /^\s*\'.*$/;
        if (/^\s*SendKeys\s*(.*?)\s*$/) {
            $_ = $1;
            while (1) {
                if    (/\G\s*\"([^ \$\"]*?)\"/gc) {$line .= " $1"}
                elsif (/\G\s*\"(.*?)\"/gc)        {$line .= " \"$1\""}
                elsif (/\G\s*_arg(\d+)/gc)        {$line .= " \$$1"}
                last unless /\G\s*\+/gc;
            }
        } elsif (/^\s*if |^\s*\S+\s*=/) {
            $line .= " []";
            $trouble = 1;
        } elsif (/^\s*\}/) {
            return;
        } elsif (/^\s*(\S+)\s+(.*)$/) {
            my $function = $1;
            my $arguments = $2;
            1 while ($arguments =~ s/_arg(\d+)/\$$1/);
            $line .= " $function($arguments)";
        }
    }
}

sub parse_keys
{
    while (<IN>) {
        $line_number++;
        next if /^\s*$/;
        if (/^\s*\}\s*\n/) {
            return;
        } elsif (/^\s*(.*?)\s*$/) {
            my $keys = $1;
            if ($keys =~ /[ \$]/) {$line .= " \"$keys\""}
            else                  {$line .= " $keys"}
        }
    }
}

sub parse_list
{
    my $first = 1;
    while (<IN>) {
        $line_number++;
        next if /^\s*$/;
        next if /^\s*\'.*$/;
        if (/^\s*\"(.*?)\"/) {
            my $item = $1;
            my $action;
            if ($item =~ /(.*)\\\\(.*)/) {
                $item = $2;
                $action = $1;
            }
            if ($item   =~ /[ \$\|]/) {$item   = "\"$item\""}
            if ($action =~ /[ \$\|]/) {$action = "\"$action\""}
            $line .= " |" unless $first;
            $line .= " $item";
            $line .= "=$action" if $action;
            $first = 0;
        } elsif (/^\s*\}/) {
            $line .= ";\n";
            return;
        } else {
            die "Expected list line\n";
        }
    }
}
