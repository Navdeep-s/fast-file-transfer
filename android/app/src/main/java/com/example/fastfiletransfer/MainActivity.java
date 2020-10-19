package com.example.fastfiletransfer;



import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;

import android.app.Activity;
import android.content.ClipData;
import android.content.ContentResolver;
import android.content.Context;
import android.content.Intent;
import android.database.Cursor;
import android.net.Uri;
import android.os.Bundle;
import android.os.Environment;
import android.os.ParcelFileDescriptor;
import android.provider.MediaStore;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.RandomAccessFile;
import java.net.Socket;
import java.net.UnknownHostException;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;
import java.nio.file.Files;
import java.util.Hashtable;
import java.util.LinkedList;
import java.util.List;

public class MainActivity extends AppCompatActivity {

    static final int SocketServerPORT = 8080;
    String dstAddress;
    int dstPort;
    static int BUFFER_SIZE = 10240;
    static String REQUEST = "o";
    static String RESPONSE = "r";
    static String PERMANENT = "p";
    static String TEMPORARY = "t";
    static String PACKET_FROM_SERVER= "s";
    static String PACKET_FROM_CLIENT = "c";
    int id_count = 0;
    List<Uri> jobs=new LinkedList<Uri>();

    DataOutputStream permanent_input;
    Hashtable<Integer, String> id_to_file_to_be_wrote=new Hashtable<Integer, String>();
    Hashtable<String, Uri> getId_to_file_to_be_send=new Hashtable<String, Uri>();

    LinearLayout loginPanel, chatPanel;

    EditText editTextUserName, editTextAddress;
    Button buttonConnect;
    TextView chatMsg, textPort;

    EditText editTextSay;
    Button buttonSend;
//    Button buttonDisconnect;

    String msgLog = "";
    String textAddress="";
    PermanentClient permanentClient = null;
    //    FileSenderThread fileSenderThread = null;
    Intent myFileIntent;
//    String sending_file_path;


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        loginPanel = (LinearLayout)findViewById(R.id.loginpanel);
//        chatPanel = (LinearLayout)findViewById(R.id.chatpanel);

        editTextUserName = (EditText) findViewById(R.id.username);
        editTextAddress = (EditText) findViewById(R.id.address);
        textPort = (TextView) findViewById(R.id.port);
        textPort.setText("port: " + SocketServerPORT);
        buttonConnect = (Button) findViewById(R.id.connect);
//        buttonDisconnect = (Button) findViewById(R.id.disconnect);
//        chatMsg = (TextView) findViewById(R.id.chatmsg);

        buttonSend  = findViewById(R.id.Send);
        buttonConnect.setOnClickListener(buttonConnectOnClickListener);
//        buttonDisconnect.setOnClickListener(buttonDisconnectOnClickListener);

//        editTextSay = (EditText)findViewById(R.id.say);
//        buttonSend = (Button)findViewById(R.id.send);

//        buttonSend.setOnClickListener(buttonSendOnClickListener);

//        Jobs_completer jobs_completer = new Jobs_completer();
//        jobs_completer.start();

    }

//    View.OnClickListener buttonDisconnectOnClickListener = new View.OnClickListener() {
//
//        @Override
//        public void onClick(View v) {
//            if(fileRecieverThread==null){
//                return;
//            }
////            fileRecieverThread.disconnect();
//        }
//
//    };

//    View.OnClickListener buttonSendOnClickListener = new View.OnClickListener() {
//
//        @Override
//        public void onClick(View v) {
//            if (editTextSay.getText().toString().equals("")) {
//                return;
//            }
//
//            if(fileRecieverThread==null){
//                return;
//            }
//
////            fileRecieverThread.sendMsg(editTextSay.getText().toString() + "\n");
//        }
//
//    };



    private class Jobs_completer extends  Thread{

        Jobs_completer(){

        }


        @Override
        public void run() {
while (true) {
    if (!jobs.isEmpty()) {
        Log.d("second_erorr","yaaho");
        while (Thread.activeCount() > 12) {
        }
        Uri file_path = jobs.get(0);
        jobs.remove(0);
        File_sender file_sender = new File_sender(file_path);
        file_sender.start();
        try {
            file_sender.join();
        } catch (InterruptedException e) {
            e.printStackTrace();
        }


    }

}



        }
    }

    View.OnClickListener buttonConnectOnClickListener = new View.OnClickListener() {

        @Override


        public void onClick(View v) {
            String textUserName = editTextUserName.getText().toString();
            if (textUserName.equals("")) {
                Toast.makeText(MainActivity.this, "Enter User Name",
                        Toast.LENGTH_LONG).show();
                return;
            }

            String textAddress = editTextAddress.getText().toString();
            if (textAddress.equals("")) {
                Toast.makeText(MainActivity.this, "Enter Addresse",
                        Toast.LENGTH_LONG).show();
                return;
            }



            dstAddress = textAddress;
            dstPort = SocketServerPORT;

            permanentClient = new PermanentClient(textAddress, SocketServerPORT);
            permanentClient.start();
        }

    };




    private class FileReciverThread extends Thread {

        String dstAddress;
        int dstPort;
        int size_of_file;
        int size_of_name;
        String name_of_file;
        int file_percentage =0;
        ProgressBar progressBar ;
        File myExternal_file ;
        int buffer_size = 1024;


        FileReciverThread(String address, int port) {
            dstAddress = address;
            dstPort = port;
        }

        @Override
        public void run() {
            Socket socket = null;
            DataInputStream dataInputStream = null;

            try {

                //Log.d("got_something","at the start of reciver thread");
                socket = new Socket(dstAddress, dstPort);
                dataInputStream = new DataInputStream(socket.getInputStream());
                DataOutputStream dataOutputStream = new DataOutputStream(socket.getOutputStream());
                Log.d("got_something","connection esatblished");

                ByteBuffer b = ByteBuffer.allocate(4);
                b.putInt(22);
                byte[] aa = b.array();
                dataOutputStream.write(aa);

//                dataOutputStream.close();

                //Log.d("got_something","just sent acknowledgement");

                byte buffer1[] = new byte[4]; //reading first 4 bytes as they contain size information of the file
                dataInputStream.readFully(buffer1);//                byte result1[] = baos1.toByteArray();
                size_of_file  = ByteBuffer.wrap(buffer1).getInt();
                Log.d("got_something","recived size of file" +  Integer.toString(size_of_file));

                byte buffer2[] = new byte[4];
                dataInputStream.readFully(buffer2);

                size_of_name=ByteBuffer.wrap(buffer2).getInt();

                byte name_buffer[] = new byte[size_of_name];
                dataInputStream.readFully(name_buffer);

                name_of_file=new String(name_buffer);

                int remaining_file = size_of_file;

                //Log.d("hello",name_of_file);
                //Log.d("hello",Integer.toString(size_of_file));
                //Log.d("hello",Integer.toString(size_of_name));


                //Log.d("got_something","trying to open a file name "+name_of_file);

                myExternal_file = new File(getExternalFilesDir(null),name_of_file);





                FileOutputStream fos = new FileOutputStream(myExternal_file);

//                //Log.d("hello","how aer you "+ Integer.toString(remaining_file) );


                MainActivity.this.runOnUiThread(new Runnable() {

                    @Override
                    public void run() {

                        progressBar = inflateProgressBar();


                    }

                });


                while (remaining_file>0) {

                    //Log.d("hello",Integer.toString(file_percentage));
                    //Log.d("hello",Integer.toString(remaining_file));



//                    //Log.d("hello","still here  "+Integer.toString(remaining_file));


//                        //Log.d("hello","kind of ");
                    int offset ;
                    if (remaining_file<buffer_size){
                        offset = remaining_file;

                    }else{
                        offset = buffer_size;
                    }


                    byte buffer[] = new byte[offset];
                    int k =dataInputStream.read(buffer);

//                    //Log.d("hello",buffer.toString());


                    fos.write(buffer,0,k);
                    remaining_file = remaining_file - k;
                    file_percentage = (int) (((float)(size_of_file - remaining_file)/(float)size_of_file)*100.0);

                    MainActivity.this.runOnUiThread(new Runnable() {

                        @Override
                        public void run() {
                            msgLog = "";
                            //            chatMsg.setText(msg//Log);
//                            loginPanel.setVisibility(View.GONE);
//                            chatPanel.setVisibility(View.VISIBLE);

                            progressBar.setProgress(file_percentage);

                        }

                    });

//                        //Log.d(Integer.toString(remaining_file),"myfile");


                }

                fos.flush();

                progressBar.setProgress(100);
                ByteBuffer b1 = ByteBuffer.allocate(4);
                b1.putInt(1);
                byte[] a = b.array();
                dataOutputStream.write(a);
                byte buffer[] = new byte[4];
                dataInputStream.read(buffer);
                fos.close();

                //Log.d("done","main_hoo");

            } catch (UnknownHostException e) {
                e.printStackTrace();
                final String eString = e.toString();
                MainActivity.this.runOnUiThread(new Runnable() {

                    @Override
                    public void run() {
                        Toast.makeText(MainActivity.this, eString, Toast.LENGTH_LONG).show();
                    }

                });
            } catch (IOException e) {
                e.printStackTrace();
                final String eString = e.toString();
                MainActivity.this.runOnUiThread(new Runnable() {

                    @Override
                    public void run() {
                        Toast.makeText(MainActivity.this, eString, Toast.LENGTH_LONG).show();
                    }

                });
            } finally {
                if (socket != null) {
                    try {
                        socket.close();
                    } catch (IOException e) {
                        // TODO Auto-generated catch block
                        e.printStackTrace();
                    }
                }

//                if (dataOutputStream != null) {
//                    try {
//                        dataOutputStream.close();
//                    } catch (IOException e) {
//                        // TODO Auto-generated catch block
//                        e.printStackTrace();
//                    }
//                }

                if (dataInputStream != null) {
                    try {
                        dataInputStream.close();
                    } catch (IOException e) {
                        // TODO Auto-generated catch block
                        e.printStackTrace();
                    }
                }

//                MainActivity.this.runOnUiThread(new Runnable() {
//
//                    @Override
//                    public void run() {
//                        loginPanel.setVisibility(View.VISIBLE);
////                        chatPanel.setVisibility(View.GONE);
//                    }
//
//                });
            }

        }

    }




    private class FileSenderThread extends Thread {

        Uri sending_file_path;
        String dstAddress;
        int dstPort;
        int buffer_size = 1024;
        long file_size;
        long remaining_size;
        String file_name ;
        ProgressBar progressBar;
        int file_percentage;

        FileSenderThread(Uri sending_file_path, String address, int port) {
            this.sending_file_path = sending_file_path;
            dstAddress = address;
            dstPort = port;
        }

        @Override
        public void run() {
            Socket socket = null;
            DataOutputStream dataOutputStream = null;

            try {
                socket = new Socket(dstAddress, dstPort);
                dataOutputStream = new DataOutputStream(
                        socket.getOutputStream());

                //Log.d("hello1","hi");
                //Log.d("hello1","hi1");
                ParcelFileDescriptor file = getContentResolver().openFileDescriptor(sending_file_path,"r");
                file_size=file.getStatSize();

                file_name = new File(sending_file_path.getPath()).getName();
                //Log.d("hello1",file_name);
                int file_name_length = file_name.length();

//               //Log.d("hello1",Long.toString(file.getStatSize()));
                file.close();
//                //Log.d("hello1",file.getName());

//                //Log.d("hello1",file.getAbsolutePath());

//                //Log.d("hello1",Long.toString(file_size));

//                file_size = file.length();
//                //Log.d("hello1",sending_file_path.getPath());


                ByteBuffer b = ByteBuffer.allocate(4);
                b.putInt(11);
                byte[] aa = b.array();
                dataOutputStream.write(aa);



                ByteBuffer bb = ByteBuffer.allocate(8);
                bb.putLong(file_size);
                byte[] a = bb.array();
//                //Log.d("hello1", a.toString());
                //Log.d("hello1",Long.toString(file_size));
                //Log.d("hello1",Long.toHexString(file_size));

                dataOutputStream.write(a);


                ByteBuffer b1 = ByteBuffer.allocate(4);
                b1.putInt(file_name_length);
                byte[] a1 = b1.array();
                dataOutputStream.write(a1);

                dataOutputStream.writeBytes(file_name);




                FileInputStream fos = (FileInputStream)getContentResolver().openInputStream(sending_file_path);
//                //Log.d("hello1","hi3");



                remaining_size = file_size;

                MainActivity.this.runOnUiThread(new Runnable() {

                    @Override
                    public void run() {

                        progressBar = inflateProgressBar();


                    }

                });

                while(remaining_size>0) {

                    byte[] buffer = new byte[buffer_size];
                    try {
                        fos.read(buffer);

                        dataOutputStream.write(buffer);
                        dataOutputStream.flush();

                        remaining_size = remaining_size - buffer_size;
                        file_percentage = (int) (((float)(file_size - remaining_size)/(float)file_size)*100.0);


                        MainActivity.this.runOnUiThread(new Runnable() {

                            @Override
                            public void run() {
//                                msg//Log = "";
                                //            chatMsg.setText(msg//Log);
//                                loginPanel.setVisibility(View.GONE);
//                                chatPanel.setVisibility(View.VISIBLE);

                                progressBar.setProgress(file_percentage);

                            }

                        });


                    } catch (Exception e) {
                        e.printStackTrace();
                    }
//                    //Log.d("hello1", buffer.toString());

                }




            } catch (UnknownHostException e) {
                e.printStackTrace();
                final String eString = e.toString();
                MainActivity.this.runOnUiThread(new Runnable() {

                    @Override
                    public void run() {
                        Toast.makeText(MainActivity.this, eString, Toast.LENGTH_LONG).show();
                    }

                });
            } catch (IOException e) {
                e.printStackTrace();
                final String eString = e.toString();
                MainActivity.this.runOnUiThread(new Runnable() {

                    @Override
                    public void run() {
                        Toast.makeText(MainActivity.this, eString, Toast.LENGTH_LONG).show();
                    }

                });
            } finally {
                if (socket != null) {
                    try {
                        socket.close();
                    } catch (IOException e) {
                        // TODO Auto-generated catch block
                        e.printStackTrace();
                    }
                }

                if (dataOutputStream != null) {
                    try {
                        dataOutputStream.close();
                    } catch (IOException e) {
                        // TODO Auto-generated catch block
                        e.printStackTrace();
                    }
                }



//                MainActivity.this.runOnUiThread(new Runnable() {
//
//                    @Override
//                    public void run() {
//                        loginPanel.setVisibility(View.VISIBLE);
//                        chatPanel.setVisibility(View.GONE);
//                    }
//
//                });
            }

        }


    }


    ProgressBar inflateProgressBar(){
        LinearLayout place1=(LinearLayout) findViewById(R.id.place);
        getLayoutInflater().inflate(R.layout.progresbar,place1);
//        Toast.makeText(this,place1.getChildCount()+"sa",Toast.LENGTH_SHORT).show();
        LinearLayout new_progress_bar_layout = (LinearLayout) place1.getChildAt(place1.getChildCount()-1);

        ProgressBar pbar=(ProgressBar) new_progress_bar_layout.getChildAt(1);
        return pbar;

    }


    public void initiate_send(View view) {
        String textUserName = editTextUserName.getText().toString();
        if (textUserName.equals("")) {
            Toast.makeText(MainActivity.this, "Enter User Name",
                    Toast.LENGTH_LONG).show();
            return;
        }

        textAddress = editTextAddress.getText().toString();
        if (textAddress.equals("")) {
            Toast.makeText(MainActivity.this, "Enter Addresse",
                    Toast.LENGTH_LONG).show();
            return;
        }

        myFileIntent= new Intent(Intent.ACTION_GET_CONTENT);
        myFileIntent.putExtra(Intent.EXTRA_ALLOW_MULTIPLE,true);
        myFileIntent.setType("*/*");
        startActivityForResult(myFileIntent, 10);

    }


    @Override
    protected void onActivityResult(int requestCode, int resultCode, @Nullable Intent data) {
        super.onActivityResult(requestCode, resultCode, data);



        if (requestCode==10){

            if(resultCode==RESULT_OK){
                try {

                    ClipData clipData = data.getClipData();
                    Log.d("nubmer",Integer.toString(clipData.getItemCount()));
                    for(int i = 0 ;i<clipData.getItemCount();i++) {





                        Uri file_path = clipData.getItemAt(i).getUri();
//                    //Log.d("hello1",sending_file_path);



//                        jobs.add(file_path);


                        File_sender file_sender = new File_sender(file_path);
                        file_sender.start();
                        file_sender.join();

                    }
                }

                catch (Exception e) {
                    Uri file_path = data.getData();
//                    Log.d("hello1",sending_file_path);

//                    jobs.add(file_path);
                    File_sender fileSenderThread = new File_sender(file_path);
                    fileSenderThread.start();
                    e.printStackTrace();
                }

            }


        }

    }



    private class File_sender extends Thread {

        Uri sending_file_path;
        long file_size;
        String file_name ;

        File_sender(Uri sending_file_path) {
            this.sending_file_path = sending_file_path;
        }

        @Override
        public void run() {
            DataOutputStream dataOutputStream = permanent_input;


            try {



                //Log.d("hello1","hi");
                //Log.d("hello1","hi1");
                ParcelFileDescriptor file = getContentResolver().openFileDescriptor(sending_file_path,"r");
                file_size=file.getStatSize();

                file_name = new File(sending_file_path.getPath()).getName();
                //Log.d("hello1",file_name);
                int file_name_length = file_name.length();

//               //Log.d("hello1",Long.toString(file.getStatSize()));
                file.close();
//                //Log.d("hello1",file.getName());

//                //Log.d("hello1",file.getAbsolutePath());

//                //Log.d("hello1",Long.toString(file_size));

//                file_size = file.length();
//                //Log.d("hello1",sending_file_path.getPath());


                ByteBuffer b = ByteBuffer.allocate(4);
                b.putInt(file_name_length);
                byte[] name_size_bytes = b.array();



                ByteBuffer bb = ByteBuffer.allocate(8);
                bb.putLong(file_size);
                byte[] file_size_bytes = bb.array();
//                //Log.d("hello1", a.toString());
                //Log.d("hello1",Long.toString(file_size));
                Log.d("second_error","file_size"+file_size+" name"+file_name+" id " + id_count);



                dataOutputStream.writeBytes(REQUEST);
                dataOutputStream.write(name_size_bytes);
                dataOutputStream.writeBytes(file_name);
                dataOutputStream.write(file_size_bytes);

                //just junk values
                dataOutputStream.write(name_size_bytes);
                dataOutputStream.write(name_size_bytes);



                getId_to_file_to_be_send.put(file_name,sending_file_path);
//                //Log.d("hello1","hi3");









            } catch (UnknownHostException e) {
                e.printStackTrace();

            } catch (IOException e) {
                e.printStackTrace();

            }

        }


    }



    private class Send_packet extends Thread {

        long starting_point;
        long file_size;
        int data_id;

        Uri sending_file_path;
        int buffer_size = BUFFER_SIZE;
        long remaining_size;
        ProgressBar progressBar;
        int file_percentage;

        Send_packet(Uri  uri_id, long starting_point , long file_size, int id) {

            this.data_id = id;
            this.sending_file_path = uri_id;
            this.starting_point = starting_point;
            this.file_size = file_size;


        }

        @Override
        public void run() {
            Socket socket = null;
            DataOutputStream dataOutputStream = null;

            try {
                socket = new Socket(dstAddress, dstPort);
                dataOutputStream = new DataOutputStream(
                        socket.getOutputStream());


                dataOutputStream.writeBytes(TEMPORARY);

                dataOutputStream.writeBytes(PACKET_FROM_CLIENT);
                Log.d("second_error",TEMPORARY+" "+PACKET_FROM_CLIENT);
                ByteBuffer b = ByteBuffer.allocate(4);
                b.putInt(data_id);
                byte[] data_buffer_id = b.array();


                ByteBuffer b1 = ByteBuffer.allocate(8);
                Log.d("second_error", "Starting point is "+starting_point);
                b1.putLong(starting_point);
                byte[] starting_point_buffer = b1.array();

                ByteBuffer b2 = ByteBuffer.allocate(8);
                b2.putLong(file_size);
                byte[] file_size_buffer = b2.array();

                dataOutputStream.write(data_buffer_id);
                dataOutputStream.write(starting_point_buffer);
                dataOutputStream.write(file_size_buffer);





                //Log.d("hello1","hi");
                //Log.d("hello1","hi1");



                FileInputStream fis = (FileInputStream)getContentResolver().openInputStream(sending_file_path);
//                //Log.d("hello1","hi3");



                remaining_size = file_size;

                fis.skip(starting_point);

                MainActivity.this.runOnUiThread(new Runnable() {

                    @Override
                    public void run() {

                        progressBar = inflateProgressBar();


                    }

                });

                while(remaining_size>0) {

                    if (remaining_size<buffer_size){
                        buffer_size = (int)remaining_size;
                    }

                    byte[] buffer = new byte[buffer_size];
                    try {
                        fis.read(buffer);

                        dataOutputStream.write(buffer);
                        dataOutputStream.flush();

                        remaining_size = remaining_size - buffer_size;
                        file_percentage = (int) (((float)(file_size - remaining_size)/(float)file_size)*100.0);


                        MainActivity.this.runOnUiThread(new Runnable() {

                            @Override
                            public void run() {
//                                msg//Log = "";
                                //            chatMsg.setText(msg//Log);
//                                loginPanel.setVisibility(View.GONE);
//                                chatPanel.setVisibility(View.VISIBLE);

                                progressBar.setProgress(file_percentage);

                            }

                        });


                    } catch (Exception e) {
                        e.printStackTrace();
                    }
//                    //Log.d("hello1", buffer.toString());

                }




            } catch (UnknownHostException e) {
                e.printStackTrace();
                final String eString = e.toString();
                MainActivity.this.runOnUiThread(new Runnable() {

                    @Override
                    public void run() {
                        Toast.makeText(MainActivity.this, eString, Toast.LENGTH_LONG).show();
                    }

                });
            } catch (IOException e) {
                e.printStackTrace();
                final String eString = e.toString();
                MainActivity.this.runOnUiThread(new Runnable() {

                    @Override
                    public void run() {
                        Toast.makeText(MainActivity.this, eString, Toast.LENGTH_LONG).show();
                    }

                });
            } finally {
                if (socket != null) {
                    try {
                        socket.close();
                    } catch (IOException e) {
                        // TODO Auto-generated catch block
                        e.printStackTrace();
                    }
                }

                if (dataOutputStream != null) {
                    try {
                        dataOutputStream.close();
                    } catch (IOException e) {
                        // TODO Auto-generated catch block
                        e.printStackTrace();
                    }
                }



//                MainActivity.this.runOnUiThread(new Runnable() {
//
//                    @Override
//                    public void run() {
//                        loginPanel.setVisibility(View.VISIBLE);
//                        chatPanel.setVisibility(View.GONE);
//                    }
//
//                });
            }

        }


    }




    private class Recieve_packet extends Thread {

        Socket client;
        int data_id;
        long starting_point;
        long file_size;



        int size_of_file;
        int size_of_name;
        String name_of_file;
        int file_percentage =0;
        ProgressBar progressBar ;
        File myExternal_file ;
        int buffer_size = BUFFER_SIZE;


        Recieve_packet(int id, long starting_point, long file_size) {
            this.data_id = id;
            this.starting_point = starting_point;
            this.file_size = file_size;

        }

        @Override
        public void run() {
            Socket socket = null;
            DataInputStream dataInputStream = null;

            try {

                //Log.d("got_something","at the start of reciver thread");
                socket = new Socket(dstAddress, dstPort);
                dataInputStream = new DataInputStream(socket.getInputStream());
                DataOutputStream dataOutputStream = new DataOutputStream(socket.getOutputStream());

                dataOutputStream.writeBytes(TEMPORARY);
                dataOutputStream.writeBytes((PACKET_FROM_SERVER));

                ByteBuffer b = ByteBuffer.allocate(4);
                b.putInt(data_id);
                byte[] data_id_buffer = b.array();


                ByteBuffer b1 = ByteBuffer.allocate(8);
                Log.d("my_error","starting_point is "+starting_point+","+file_size+","+data_id);
                b1.putLong(starting_point);
                byte[] starting_point_buffer = b1.array();

                ByteBuffer b2 = ByteBuffer.allocate(8);
                b2.putLong(file_size);
                byte[] file_size_buffer = b2.array();


                dataOutputStream.write(data_id_buffer);
                dataOutputStream.write(starting_point_buffer);
                dataOutputStream.write(file_size_buffer);

                byte[] temp_buffer = new byte[20] ;

                dataInputStream.readFully(temp_buffer);



                name_of_file = id_to_file_to_be_wrote.get(data_id);

                myExternal_file = new File(getExternalFilesDir(null),name_of_file);

                if(!myExternal_file.exists()){

                    myExternal_file.createNewFile();
                }



                RandomAccessFile raf = new RandomAccessFile(myExternal_file,"rw");

                raf.seek(starting_point);

//                //Log.d("hello","how aer you "+ Integer.toString(remaining_file) );


                MainActivity.this.runOnUiThread(new Runnable() {

                    @Override
                    public void run() {

                        progressBar = inflateProgressBar();


                    }

                });

                long remaining_file = file_size;



                while (remaining_file>0) {

                    //Log.d("hello",Integer.toString(file_percentage));
                    //Log.d("hello",Integer.toString(remaining_file));



//                    //Log.d("hello","still here  "+Integer.toString(remaining_file));


//                        //Log.d("hello","kind of ");
                    int offset ;
                    if (remaining_file<buffer_size){
                        offset =  (int)remaining_file;

                    }else{
                        offset = buffer_size;
                    }


                    byte[] buffer = new byte[offset];
                    int k =dataInputStream.read(buffer);


//                    //Log.d("hello",buffer.toString());


                    raf.write(buffer,0,k);
                    remaining_file = remaining_file - k;
                    file_percentage = (int) (((float)(file_size - remaining_file)/(float)file_size)*100.0);
//                    Log.d("my_error","File percentage"+file_percentage);
                    MainActivity.this.runOnUiThread(new Runnable() {

                        @Override
                        public void run() {
                            msgLog = "";
                            //            chatMsg.setText(msg//Log);
//                            loginPanel.setVisibility(View.GONE);
//                            chatPanel.setVisibility(View.VISIBLE);

                            progressBar.setProgress(file_percentage);

                        }

                    });

//                        //Log.d(Integer.toString(remaining_file),"myfile");


                }

                raf.close();


                progressBar.setProgress(100);

                //Log.d("done","main_hoo");

            } catch (UnknownHostException e) {
                e.printStackTrace();
                final String eString = e.toString();
                MainActivity.this.runOnUiThread(new Runnable() {

                    @Override
                    public void run() {
                        Toast.makeText(MainActivity.this, eString, Toast.LENGTH_LONG).show();
                    }

                });
            } catch (IOException e) {
                e.printStackTrace();
                final String eString = e.toString();
                MainActivity.this.runOnUiThread(new Runnable() {

                    @Override
                    public void run() {
                        Toast.makeText(MainActivity.this, eString, Toast.LENGTH_LONG).show();
                    }

                });
            } finally {
                if (socket != null) {
                    try {
                        socket.close();
                    } catch (IOException e) {
                        // TODO Auto-generated catch block
                        e.printStackTrace();
                    }
                }

//                if (dataOutputStream != null) {
//                    try {
//                        dataOutputStream.close();
//                    } catch (IOException e) {
//                        // TODO Auto-generated catch block
//                        e.printStackTrace();
//                    }
//                }

                if (dataInputStream != null) {
                    try {
                        dataInputStream.close();
                    } catch (IOException e) {
                        // TODO Auto-generated catch block
                        e.printStackTrace();
                    }
                }

//                MainActivity.this.runOnUiThread(new Runnable() {
//
//                    @Override
//                    public void run() {
//                        loginPanel.setVisibility(View.VISIBLE);
////                        chatPanel.setVisibility(View.GONE);
//                    }
//
//                });
            }

        }

    }







    private class PermanentClient extends Thread{
        String acknowledgement=PERMANENT;
        String dstAddress;
        int dstPort;

//        boolean goOut = false;

        PermanentClient(String address, int port) {
            this.dstAddress = address;
            this.dstPort = port;
        }

        @Override
        public void run() {
            Socket socket = null;
            DataOutputStream dataOutputStream = null;
            DataInputStream dataInputStream = null;

            try {
                socket = new Socket(dstAddress, dstPort);
                dataOutputStream = new DataOutputStream(
                        socket.getOutputStream());
                dataInputStream = new DataInputStream(socket.getInputStream());

                permanent_input = dataOutputStream;
                dataOutputStream.writeBytes(acknowledgement);


//                ByteBuffer b = ByteBuffer.allocate(4);
//                b.putInt(33);
//                byte[] aa = b.array();
//                dataOutputStream.write(aa);

                runOnUiThread(new Runnable() {
                    @Override
                    public void run() {
                        buttonSend.setVisibility(View.VISIBLE);
                        buttonConnect.setText("CONNECTED");
                        buttonConnect.setEnabled(false);

                    }
                });

                //Log.d("got_something","hello there");

                while (true) {
                    //Log.d("got_something","starting to recieve");
                    byte[] buffer = new byte[1];
                    dataInputStream.read(buffer);
                    String message_type = new String(buffer);


                    if(message_type.equals(RESPONSE)){

                        byte[] buffer1 = new byte[4];
                        //reading name size
                        dataInputStream.readFully(buffer1);
                        int name_size  = ByteBuffer.wrap(buffer1).getInt();

                        //reading name of the file
                        byte[] name_buffer = new byte[name_size];
                        dataInputStream.readFully(name_buffer);
                        String name = new String(name_buffer);

                        //reading file size
                        byte[] file_size_buffer = new byte[8];
                        dataInputStream.readFully(file_size_buffer);
                        long file_size = ByteBuffer.wrap(file_size_buffer).getLong();

                        //reading id
                        dataInputStream.readFully(buffer1);
                        int id = ByteBuffer.wrap(buffer1).getInt();;

                        //reading number_of_sockets
                        dataInputStream.readFully(buffer1);
                        int number_of_sockets= ByteBuffer.wrap(buffer1).getInt();


                        //adding he value into hash
                        Uri uri_id = getId_to_file_to_be_send.get(name);
                        Log.d("second_error","finally came to size calculation");

                        long data_length = file_size/number_of_sockets;

                        for (int k = 0;k<number_of_sockets-1;k++){


                            //todo
                            long starting_point  = k*data_length;

                            Send_packet packet_sender = new Send_packet(uri_id, starting_point,data_length,id);
                            packet_sender.start();

                            //start a send_packet socket thread
                        }

                        long remaining_data = file_size - data_length*(number_of_sockets-1);
                        Send_packet packet_sender = new Send_packet(uri_id, data_length*(number_of_sockets-1),remaining_data,id);
                        packet_sender.start();




                    }else if(message_type.equals(REQUEST)){

                        Log.d("my_error","entering handling request mode");


                        byte[] name_size_bytes = new byte[4];
                        //reading name size
                        dataInputStream.readFully(name_size_bytes);
                        int name_size  = ByteBuffer.wrap(name_size_bytes).getInt();

                        //reading name of the file
                        byte[] name_buffer = new byte[name_size];
                        dataInputStream.readFully(name_buffer);
                        String name = new String(name_buffer);

                        //reading file size
                        byte[] file_size_buffer = new byte[8];
                        dataInputStream.readFully(file_size_buffer);
                        long file_size = ByteBuffer.wrap(file_size_buffer).getLong();


                        //reading id
                        byte[] id_bytes = new byte[4];
                        dataInputStream.readFully(id_bytes);

                        //reading number_of_sockets
                        byte[] socket_bytes = new byte[4];
                        dataInputStream.readFully(socket_bytes);

                        int number_of_sockets = ByteBuffer.wrap(socket_bytes).getInt();

                        Log.d("my_error",id_count+name);

                        id_to_file_to_be_wrote.put(id_count,name);
                        id_count++;

                        ByteBuffer id = ByteBuffer.allocate(4);
                        id.putInt(id_count-1);
                        byte[] id_buffer = id.array();


                        dataOutputStream.writeBytes(RESPONSE);
                        dataOutputStream.write(name_size_bytes);
                        dataOutputStream.write(name_buffer);
                        dataOutputStream.write(file_size_buffer);
                        dataOutputStream.write(id_buffer);
                        dataOutputStream.write(socket_bytes);


                        long data_length = file_size/number_of_sockets;


                        for (int k = 0;k<number_of_sockets-1;k++){



                            long starting_point  = k*data_length;

                            Recieve_packet packet_sender = new Recieve_packet(id_count-1, starting_point,data_length);
                            packet_sender.start();

                            //start a send_packet socket thread
                        }

                        long remaining_data = file_size - data_length*(number_of_sockets-1);
                        Recieve_packet packet_sender = new Recieve_packet(id_count-1, data_length*(number_of_sockets-1),remaining_data);
                        packet_sender.start();





                    }else{
                        Log.d("my_error",message_type);

                    }


                    //Log.d("got_something",buffer.toString());


//                    int number_of_file = ByteBuffer.wrap(buffer).getInt();
//
//                    //Log.d("got_something",Integer.toString(number_of_file));
//                    for(int k =0 ; k<number_of_file ;k++){
//
//
//                        //Log.d("got_something","starting reciver thread");
//                        FileReciverThread fileRecieverThread = new FileReciverThread(dstAddress, dstPort);
//                        fileRecieverThread.start();
//
//                    }
//
//
//                    if(number_of_file == 0){
//                        break;
//                    }
                }



            } catch (UnknownHostException e) {
                e.printStackTrace();
                final String eString = e.toString();
                MainActivity.this.runOnUiThread(new Runnable() {

                    @Override
                    public void run() {
                        Toast.makeText(MainActivity.this, eString, Toast.LENGTH_LONG).show();
                    }

                });
            } catch (IOException e) {
                e.printStackTrace();
                final String eString = e.toString();
                MainActivity.this.runOnUiThread(new Runnable() {

                    @Override
                    public void run() {
                        Toast.makeText(MainActivity.this, eString, Toast.LENGTH_LONG).show();
                    }

                });
            } finally {
                if (socket != null) {
                    try {
                        socket.close();
                    } catch (IOException e) {
                        // TODO Auto-generated catch block
                        e.printStackTrace();
                    }


                    runOnUiThread(new Runnable() {
                        @Override
                        public void run() {
                            buttonSend.setVisibility(View.GONE);
                            buttonConnect.setText("CONNECT");
                            buttonConnect.setEnabled(true);

                        }
                    });
                }

                if (dataOutputStream != null) {
                    try {
                        dataOutputStream.close();
                    } catch (IOException e) {
                        // TODO Auto-generated catch block
                        e.printStackTrace();
                    }
                }

                if (dataInputStream != null) {
                    try {
                        dataInputStream.close();
                    } catch (IOException e) {
                        // TODO Auto-generated catch block
                        e.printStackTrace();
                    }
                }

            }

        }


    }

}







