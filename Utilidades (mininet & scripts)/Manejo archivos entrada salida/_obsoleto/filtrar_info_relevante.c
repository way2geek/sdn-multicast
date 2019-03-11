#include <stdio.h>
#include <string.h>
#include <stdlib.h>

void manejoError(char * msg){
  printf("Error: %s\n", msg);
  exit(EXIT_FAILURE);
}

int main(int argc, char * argv[]) {

  char * linea = NULL;
	size_t leido =0;
	size_t tamanoLinea=0;

  char * texto_descarte1= "packet in";
  char * texto_descarte2= "packet out";
  FILE * input = NULL;
  int i=0;
  input=fopen("test2.txt","r");

  if (input!=NULL){
    printf("Voy a leer archivo\n");

    leido = getline(&linea, &tamanoLinea, input);
    printf("\tLei = %ld\n", leido);
    printf("\t \tLinea leida = %s",linea);

    while (leido>0 ){
      printf("Entre al while\n");

      leido = getline(&linea, &tamanoLinea, input);
      printf("%d\t",i);
      i++;
    }
    printf("\t\t\tsali del while\n");
  }

  printf("\t\tFin del programa\n");
  return 1;
}






// if (strstr(linea,texto_descarte1)==NULL || strstr(linea,texto_descarte2)==NULL){
//   printf("\t\t\tSTR STR = %s",strstr(linea,texto_descarte1));
//   printf("Linea IGMP !! \n");
//   //Enviar a archivo de salida IGMP
// }
// else{
//   printf("\t\t\tSTR STR = %s \n ",strstr(linea,texto_descarte1));
//   printf("Material openflow !! \n");
//   //Enviar a archivo de salida Openflow
// }
