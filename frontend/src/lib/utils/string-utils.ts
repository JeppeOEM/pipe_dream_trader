export function findStringIndex(stringToFind: string, stringArray: Array<string>) {

  const index = stringArray.indexOf(stringToFind);

  if (index === -1) {
    return -1
  }
  return index
}


