FROM archlinux:20200908 as release

RUN pacman -Syu base-devel git --noconfirm
RUN useradd -m app -g users -G wheel \
&& echo "%wheel ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

USER app
WORKDIR /home/app

RUN git clone "https://aur.archlinux.org/yay.git"
RUN cd yay && yes | makepkg -sicr
RUN rm -rf yay

CMD sh


FROM release as debug

RUN sudo pacman -S nano man man-db --noconfirm

#docker build . -t temp --target debug
#docker run -it temp
