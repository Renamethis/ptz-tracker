#include<iostream>
#include<algorithm>
#include<fstream>
#include<chrono>
#include <time.h>
#include<opencv2/core/core.hpp>
#include "System.h"
#include "Osmap.h"
#include <fstream>
#include "Converter.h"
#include <cmath>
#include <zmq.hpp>
#define _USE_MATH_DEFINES
using namespace std;
using namespace cv;
inline bool ifexists (const string& name) {
    ifstream f(name.c_str());
    return f.good();
}
int main(int argc, char **argv)
{
    zmq::context_t context{1};
    zmq::socket_t socket{context, zmq::socket_type::req};
    socket.connect("tcp://localhost:5555");
    string rtsp_url = argv[3];
    string gst_url = "rtspsrc location=" + rtsp_url + " ! rtph264depay ! decodebin ! videoconvert ! appsink";
    VideoCapture cap(gst_url);
    cv::Mat frame;
    string FileName = "/home/ivan/Documents/ORB_SLAM2/orb_module/map/NewMap";
    time_t time0;   // create timers.
    time_t time1;
    time(&time0);   // get current time.
    if(argc != 4) {
        cerr << endl << "Usage: ./orb_module path_to_vocabulary path_to_config" << endl;
        return 1;
    }
    const auto p1 = std::chrono::system_clock::now();
    ORB_SLAM2::System SLAM(argv[1],argv[2],ORB_SLAM2::System::MONOCULAR,true);
    ORB_SLAM2::Osmap osmap = ORB_SLAM2::Osmap(SLAM);
    osmap.verbose = true;
    osmap.options.set(ORB_SLAM2::Osmap::ONLY_MAPPOINTS_FEATURES, 1);
    if (!cap.isOpened() || !cap.read(frame)) {
	     cout << "Something wrong with your rtsp-stream" << endl;
       return 0;
    }
    cv::Mat Tcw = SLAM.TrackMonocular(frame, 0);
    if(ifexists(FileName + ".yaml"))
    	osmap.mapLoad(FileName + ".yaml");
    while(cap.isOpened()) {
      time(&time1);
      if (!cap.read(frame)) {
        cout << "Stream was broken" << endl;
        break;
      }
      double seconds = time1 - time0;
      cv::resize(frame, frame, cv::Size(720, 640), 0, 0);
      cv::Mat Tcw = SLAM.TrackMonocular(frame, seconds);
      if (!Tcw.empty()) {
        cv::Mat Rwc = Tcw.rowRange(0,3).colRange(0,3).t(); // Rotation information
        cv::Mat twc = -Rwc*Tcw.rowRange(0,3).col(3); // translation information
        auto ang = ORB_SLAM2::Converter::toVector3d(Rwc);
        auto pos = ORB_SLAM2::Converter::toVector3d(twc);
        putText(frame, "(" + to_string(pos[0]) + ", " + to_string(pos[1]) + ", " +
        to_string(pos[2]) + ")",
        cv::Point(50, frame.rows-50), cv::FONT_HERSHEY_DUPLEX, 0.9,
        CV_RGB(118, 185, 0), 1);
        string message = (to_string(ang[0]) + " " + to_string(ang[1]) + " " + to_string(ang[2])
        + "|" + to_string(pos[0]) + " " + to_string(pos[1]) + " " + to_string(pos[2]));
        socket.send(zmq::buffer(message), zmq::send_flags::none);
        zmq::message_t reply{};
        socket.recv(reply, zmq::recv_flags::none);
        string rpl = string(static_cast<char*>(reply.data()), reply.size());
        if(rpl != std::string("Ok")) {
          cout << "Problem with getting reply from tracker" << endl;
          return 0;
        }
      }
      if((char)waitKey(1) == 27) {
        osmap.mapSave(FileName);
        break;
      }
    }
    SLAM.Shutdown();
    cap.release();
    destroyAllWindows();
    return 0;
}
