/**
 * (C) Thomas Weber 2024 tom-vibrant@gmx.de
 * 
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>. 
 */

class DemoLinter {

    /**
     * Uses this fork of filbert which can parse kwargs: https://github.com/janakaud/filbert
     */
    getAnnotations(source) {
        try {
            filbert.parse(source);

            return [];
    
        } catch (e) {
            return [
                {
                    message: e.message,
                    from: {
                        line: e.loc.line - 1
                    },
                    to: {
                        line: e.loc.line
                    },
                    severity: "error"
                }
            ];
        }
    }
}